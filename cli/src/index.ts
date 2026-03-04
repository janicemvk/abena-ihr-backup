#!/usr/bin/env node
/**
 * abena-cli - ABENA node deployment and operations
 */

import { Command } from 'commander';
import { deployCommand } from './commands/deploy';
import { joinNetworkCommand } from './commands/join-network';
import { backupCommand } from './commands/backup';
import { restoreCommand } from './commands/restore';
import { statusCommand } from './commands/status';

const program = new Command();

program
  .name('abena-cli')
  .description('ABENA blockchain node deployment and operations')
  .version('4.0.0-dev');

program.addCommand(deployCommand());
program.addCommand(joinNetworkCommand());
program.addCommand(backupCommand());
program.addCommand(restoreCommand());
program.addCommand(statusCommand());

program.parse();
