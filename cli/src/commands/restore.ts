import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as path from 'path';
import * as fs from 'fs-extra';
import { execSync } from 'child_process';

async function downloadFromS3(s3Uri: string, localPath: string): Promise<void> {
  const { S3Client, GetObjectCommand } = require('@aws-sdk/client-s3');
  const client = new S3Client({});
  const match = s3Uri.match(/s3:\/\/([^/]+)\/(.+)/);
  if (!match) throw new Error('Invalid S3 URI');
  const [, bucket, key] = match;
  const resp = await client.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
  const body = resp.Body;
  if (!body) throw new Error('Empty S3 response');
  const buf = await body.transformToByteArray();
  await fs.writeFile(localPath, Buffer.from(buf));
}

export function restoreCommand(): Command {
  const cmd = new Command('restore')
    .description('Restore ABENA chain from backup')
    .requiredOption('-f, --from <path>', 'Backup: snapshot-YYYYMMDD or s3://bucket/key')
    .option('-b, --base-path <path>', 'Node base path', './abena-data/node')
    .option('--force', 'Overwrite existing data', false)
    .action(async (opts) => {
      const spinner = ora('Restoring from backup...').start();
      const basePath = path.resolve(opts.basePath);
      const chainsPath = path.join(basePath, 'chains', 'development');
      const isS3 = opts.from.startsWith('s3://');

      try {
        if (await fs.pathExists(chainsPath) && !opts.force) {
          throw new Error(`Chains path exists. Use --force to overwrite.`);
        }

        let archivePath: string;
        if (isS3) {
          archivePath = path.join(process.cwd(), '.abena-restore-tmp', 'backup.tar.gz');
          await fs.ensureDir(path.dirname(archivePath));
          spinner.text = 'Downloading from S3...';
          await downloadFromS3(opts.from, archivePath);
        } else {
          const candidate = path.resolve(opts.from);
          if (!opts.from.endsWith('.tar.gz')) {
            archivePath = path.join(process.cwd(), `${opts.from}.tar.gz`);
            if (!(await fs.pathExists(archivePath))) {
              archivePath = candidate;
            }
          } else {
            archivePath = await fs.pathExists(candidate) ? candidate : path.join(process.cwd(), opts.from);
          }
          if (!(await fs.pathExists(archivePath))) {
            throw new Error(`Backup not found: ${archivePath}`);
          }
        }

        spinner.text = 'Extracting...';
        await fs.ensureDir(path.dirname(chainsPath));
        if (await fs.pathExists(chainsPath)) await fs.remove(chainsPath);
        const tmpExtract = path.join(process.cwd(), '.abena-restore-tmp', 'extract');
        await fs.ensureDir(tmpExtract);
        execSync(`tar -xzf "${archivePath}" -C "${tmpExtract}"`, { stdio: 'pipe' });
        const extracted = (await fs.readdir(tmpExtract))[0];
        if (extracted) {
          const srcChains = path.join(tmpExtract, extracted, 'chains');
          if (await fs.pathExists(srcChains)) {
            await fs.copy(srcChains, path.join(path.dirname(chainsPath)));
          } else {
            await fs.copy(path.join(tmpExtract, extracted), chainsPath);
          }
        }
        await fs.remove(tmpExtract);
        if (isS3) await fs.remove(archivePath);

        spinner.succeed(chalk.green('Restore complete'));
        console.log(chalk.cyan('Restored to:') + ` ${chainsPath}`);
      } catch (err) {
        spinner.fail(chalk.red('Restore failed'));
        console.error(err);
        process.exit(1);
      }
    });

  return cmd;
}
