import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as path from 'path';
import * as fs from 'fs-extra';
import { execSync } from 'child_process';

async function uploadToS3(dest: string, filePath: string): Promise<void> {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');
  const client = new S3Client({});
  const match = dest.match(/s3:\/\/([^/]+)\/(.+)/);
  if (!match) throw new Error('Invalid S3 destination: use s3://bucket/key');
  const [, bucket, key] = match;
  const body = await fs.readFile(filePath);
  await client.send(
    new PutObjectCommand({
      Bucket: bucket,
      Key: key,
      Body: body,
    })
  );
}

export function backupCommand(): Command {
  const cmd = new Command('backup')
    .description('Backup ABENA chain database')
    .requiredOption('-d, --destination <path>', 'Destination: s3://bucket/key or /local/path')
    .option('-b, --base-path <path>', 'Node base path', './abena-data/node')
    .option('-n, --name <name>', 'Backup name', '')
    .action(async (opts) => {
      const spinner = ora('Creating backup...').start();
      const basePath = path.resolve(opts.basePath);
      const chainsPath = path.join(basePath, 'chains', 'development');
      const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      const name = opts.name || `snapshot-${timestamp}`;
      const isS3 = opts.destination.startsWith('s3://');

      try {
        if (!(await fs.pathExists(chainsPath))) {
          throw new Error(`Chains path not found: ${chainsPath}. Start the node first to create it.`);
        }

        const tmpDir = path.join(process.cwd(), '.abena-backup-tmp', name);
        await fs.ensureDir(tmpDir);
        await fs.copy(chainsPath, path.join(tmpDir, 'chains'));

        const archivePath = path.join(process.cwd(), `${name}.tar.gz`);
        try {
          execSync(`tar -czf "${archivePath}" -C "${path.dirname(tmpDir)}" "${name}"`, {
            stdio: 'pipe',
          });
        } catch {
          spinner.warn(chalk.yellow('tar not found, skipping compression'));
        }

        const outPath = archivePath;
        if (isS3 && (await fs.pathExists(archivePath))) {
          spinner.text = 'Uploading to S3...';
          const [bucket, ...keyParts] = opts.destination.replace(/^s3:\/\//, '').split('/');
          const key = keyParts.length ? (keyParts.join('/').endsWith('/') ? `${keyParts.join('/')}${name}.tar.gz` : keyParts.join('/')) : `${name}.tar.gz`;
          await uploadToS3(`s3://${bucket}/${key}`, outPath);
          await fs.remove(path.dirname(tmpDir));
          if (await fs.pathExists(archivePath)) await fs.remove(archivePath);
        } else {
          const destDir = path.resolve(opts.destination);
          await fs.ensureDir(destDir);
          const dest = path.join(destDir, `${name}.tar.gz`);
          if (await fs.pathExists(archivePath)) {
            await fs.move(archivePath, dest, { overwrite: true });
          }
          await fs.remove(path.dirname(tmpDir));
          spinner.succeed(chalk.green('Backup complete'));
          console.log(chalk.cyan('Saved:') + ` ${dest}`);
          return;
        }

        spinner.succeed(chalk.green('Backup complete'));
        console.log(chalk.cyan('Saved:') + ` ${opts.destination}`);
      } catch (err) {
        spinner.fail(chalk.red('Backup failed'));
        console.error(err);
        process.exit(1);
      }
    });

  return cmd;
}
