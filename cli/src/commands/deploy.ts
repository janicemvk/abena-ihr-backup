import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as path from 'path';
import * as fs from 'fs-extra';

export function deployCommand(): Command {
  const cmd = new Command('deploy')
    .description('Deploy ABENA node for hospital, validator, or RPC')
    .option('-t, --type <type>', 'Node type: hospital, validator, rpc', 'hospital')
    .option('-o, --org <name>', 'Organization name (e.g. "Mayo Clinic")', '')
    .option('-d, --data-dir <path>', 'Data directory', './abena-data')
    .option('--chain <chain>', 'Chain: dev, local, or path to chain spec', 'dev')
    .option('--base-path <path>', 'Base path for node', '')
    .action(async (opts) => {
      const spinner = ora('Deploying ABENA node...').start();
      const dataDir = path.resolve(opts.dataDir);
      const basePath = opts.basePath || path.join(dataDir, 'node');

      try {
        await fs.ensureDir(basePath);
        await fs.ensureDir(path.join(basePath, 'chains'));

        const config = {
          type: opts.type,
          org: opts.org,
          chain: opts.chain,
          basePath,
          dataDir,
        };

        const configPath = path.join(basePath, 'deploy-config.json');
        await fs.writeJson(configPath, config, { spaces: 2 });

        spinner.succeed(chalk.green('ABENA node deployment configured'));
        console.log(chalk.cyan('\nConfiguration:'));
        console.log(`  Type:      ${config.type}`);
        console.log(`  Org:       ${config.org || '(not set)'}`);
        console.log(`  Chain:     ${config.chain}`);
        console.log(`  Data dir:  ${config.basePath}`);
        console.log(chalk.yellow('\nTo start the node, run from the ABENA Blockchain repo:'));
        console.log(
          `  cargo run -p abena-node -- --base-path ${basePath} --chain ${opts.chain}`
        );
      } catch (err) {
        spinner.fail(chalk.red('Deploy failed'));
        console.error(err);
        process.exit(1);
      }
    });

  return cmd;
}
