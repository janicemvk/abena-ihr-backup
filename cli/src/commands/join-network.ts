import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as path from 'path';
import * as fs from 'fs-extra';

const CONSORTIUM_PRESETS: Record<string, { bootnodes?: string[] }> = {
  'us-healthcare': {
    bootnodes: [], // Add real bootnodes when available
  },
  dev: {
    bootnodes: [],
  },
  local: {
    bootnodes: [],
  },
};

export function joinNetworkCommand(): Command {
  const cmd = new Command('join-network')
    .description('Join ABENA consortium network')
    .option('-c, --consortium <name>', 'Consortium: us-healthcare, dev, local', 'dev')
    .option('-v, --validator', 'Run as validator (requires keys)')
    .option('-b, --base-path <path>', 'Node base path', './abena-data/node')
    .action(async (opts) => {
      const spinner = ora('Configuring network join...').start();
      const basePath = path.resolve(opts.basePath);

      try {
        const preset = CONSORTIUM_PRESETS[opts.consortium] || CONSORTIUM_PRESETS.dev;
        await fs.ensureDir(basePath);

        const configPath = path.join(basePath, 'network-config.json');
        await fs.writeJson(configPath, {
          consortium: opts.consortium,
          validator: opts.validator,
          bootnodes: preset.bootnodes,
        }, { spaces: 2 });

        spinner.succeed(chalk.green('Network configuration saved'));
        console.log(chalk.cyan('\nConsortium:') + ` ${opts.consortium}`);
        console.log(chalk.cyan('Validator:') + ` ${opts.validator ? 'yes' : 'no'}`);
        if (preset.bootnodes?.length) {
          console.log(chalk.cyan('Bootnodes:') + ` ${preset.bootnodes.length} configured`);
        }
        console.log(chalk.yellow('\nStart node with:'));
        const bootOpt = preset.bootnodes?.length
          ? ` --bootnodes ${preset.bootnodes.join(',')}`
          : '';
        console.log(`  cargo run -p abena-node -- --base-path ${basePath}${bootOpt}`);
      } catch (err) {
        spinner.fail(chalk.red('Join network failed'));
        console.error(err);
        process.exit(1);
      }
    });

  return cmd;
}
