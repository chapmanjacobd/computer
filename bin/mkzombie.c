/*
 * mkzombie - make zombie processes. Unix/Linux.
 *
 * This program creates one or more zombies and a daemon their leader.
 * It can be used to replenish system zombies, or to feed the init monster.
 *
 * 23-Jun-2005, ver 0.80
 *
 * USAGE:	mkzombie [-f] [number]
 *
 * The -f option feeds the zombies to init. On systems where init does not
 * eat zombies, the -f option will create persistant zombies.
 *
 * COPYRIGHT: Copyright (c) 2005 Brendan Gregg.
 *
 *  This program is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  as published by the Free Software Foundation; either version 2
 *  of the License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software Foundation,
 *  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 *
 *  (http://www.gnu.org/copyleft/gpl.html)
 *
 * 23-Jun-2005	Brendan Gregg	Created this.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>

/* print usage and exit */
static void
usage()
{
	(void) fprintf(stderr, "USAGE: mkzombie [-f] [number]\n");
	exit(1);
}

/* main program */
int
main(int argc, char *argv[])
{
	int 	zombies = 1;		/* default number of zombies */
	int 	feed = 0;		/* feed the init monster */
	int 	i;			/* counter */
	pid_t	pid;			/* child process id */

	/*
	 * Process arguments
	 */
	if (argc > 3) usage();
	for (i = 1; i < argc; i++) {

		if (strcmp(argv[i], "-h") == 0)
			usage();
		if (strcmp(argv[i], "-f") == 0)
			feed = 1;
		else
			zombies = atoi(argv[i]);
	}

	/*
	 * Create Zombies
	 */
	for (i = 0; i < zombies; i++) {

		pid = fork();
		switch (pid) {
			case 0:
				/* don't exit too soon */
				(void) usleep(10000);
				(void) exit(0);
				break;
			case -1:
				(void) perror("fork failed: ");
				exit(1);
				break;
		}
	}

	/*
	 * Halt parent
	 */
	if (feed)
		(void) kill(getpid(), 9);
	else
		(void) kill(getpid(), 23);

	return (0);
}
