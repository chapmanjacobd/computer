#!/usr/bin/env python3

# xdi - xdelta3 wrapper
# ed <irc.rizon.net>, MIT-licensed, https://github.com/9001/usr-local-bin
#
# expects filenames like
#   w7pos.qcow2.aaa.spice.cfg  (3rd "snapshot" of some disk image)
#   w7pos.qcow2.aa.fstrim      (2nd snap; makes a downgrade patch)
#
# produces patch names like
#   w7pos.qcow2.aaa.spice.cfg.xd3.aa.fstrim
#
# input files must be pixz or xz compressed (pixz is way faster)


import re
import os
import sys
import time
import hashlib
import tempfile
import threading
import subprocess as sp
from datetime import datetime


try:
	p = sp.Popen(['pixz', '-h'], stdout=sp.PIPE, stderr=sp.PIPE)
	p.communicate()
	HAVE_PIXZ = p.returncode == 2
except:
	HAVE_PIXZ = False
#HAVE_PIXZ = False


bintmp = os.path.join(tempfile.gettempdir(), 'xdi-bin')


def eprint(*args, **kwargs):
	kwargs['file'] = sys.stderr
	print(*args, **kwargs)


def speedfilter(f, sz):
	t0 = time.time()
	t_last = 0
	ndone = 0
	ctr = 0
	while True:
		buf = f.read(512 * 1024)
		if not buf:
			break
		
		yield buf
		ndone += len(buf)
		ctr += 1
		if ctr >= 10:
			ctr = 0
			t = time.time()
			if t - t_last < 0.1:
				continue
			
			if t_last == 0:
				eprint()

			t_last = t
			td = t - t0
			perc = 0
			if sz > 0:
				perc = (ndone * 100. / sz)
			
			spd = (ndone * 1.0 / td) / (1024 * 1024)
			eprint('\033[A  {:.0f} MiB of {:.0f} MiB, {:.2f}%, {:.2f} MiB/s  '.format(
				ndone / (1024*1024), sz / (1024*1024), perc, spd))


def hash_fobj(f, sz):
	hasher = hashlib.sha1()
	for buf in speedfilter(f, sz):
		hasher.update(buf)
	
	return hasher.hexdigest()


def getsize(fp):
	if HAVE_PIXZ:
		cmd = ['pixz', '-lt', fp]
	else:
		cmd = ['xz', '-lv', fp]
	
	p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
	so, se = p.communicate()
	txt = (so + se).decode('utf-8').split('\n')
	ret = 0
	#eprint(txt)
	if HAVE_PIXZ:
		for ln in txt:
			try:
				a, b = ln.split('/')
				ret += int(b.strip())
			except:
				pass
	else:
		ptn = re.compile(r'^[ \t]*1[ \t]*[0-9]+[ \t]*[0-9]+[ \t]*[0-9]+[ \t]*[0-9]+[ \t]*([0-9]+)')
		on = False
		for ln in txt:
			if ln == '  Blocks:':
				on = True
			
			m = ptn.match(ln)
			if not on or not m:
				continue
			
			ret += int(m.group(1))
	
	return ret


def write_stdin(fp, sz, stdin):
	for buf in speedfilter(fp, sz):
		stdin.write(buf)

	stdin.close()


def unpack(fp):
	if HAVE_PIXZ:
		cmd = ['pixz', '-dtki', fp]
	else:
		cmd = ['xz', '-dckT0', fp]
	
	return sp.Popen(cmd, stdout=sp.PIPE)


def create_patch(fp1, fp2, rm):
	for fp in [fp1, fp2]:
		if not os.path.isfile(fp):
			eprint('file does not exist: {}'.format(fp))
			sys.exit(1)
	
	ofs = 0
	for n in range(len(fp1)):
		if fp1[n] != fp2[n]:
			n -= 1
			break
	
	while fp1[n] not in ['.', '-']:
		n -= 1
	
	ofn = '{}.xd3.{}'.format(fp1, fp2[n+1:])
	if os.path.exists(ofn):
		eprint('target exists: {}'.format(ofn))
		sys.exit(1)
	
	xdi = '1\n'
	for fp in [fp1, fp2]:
		sr = os.stat(fp)

		eprint('hashing {} (compressed)'.format(fp))
		with open(fp, 'rb', 512*1024) as f:
			cko = hash_fobj(f, sr.st_size)
		
		eprint('hashing {} (inflated)'.format(fp))
		p = unpack(fp)
		cki = hash_fobj(p.stdout, getsize(fp))

		timestr = datetime.utcfromtimestamp(sr.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
		xdi += '{:6o} {} {:12} {:12} {} {} {}\n'.format(
			sr.st_mode, timestr, sr.st_size, getsize(fp), cko, cki, fp)

		#eprint(xdi)
	
	eprint('creating {}'.format(ofn))
	with open(ofn + '.xdi', 'wb') as f:
		f.write(xdi.encode('utf-8'))
	
	with open(ofn, 'wb', 512*1024) as fo:
		if HAVE_PIXZ:
			cmd = ['pixz', '-7tk']
		else:
			cmd = ['xz', '-cze7T0']
		
		env = os.environ.copy()
		env['PATH'] = str('{}:{}'.format(bintmp, env['PATH']))
		
		with open(fp2, 'rb', 512*1024) as fi:
			p1 = sp.Popen(['xdelta3', '-eRs', fp1], stdin=sp.PIPE, stdout=sp.PIPE, env=env)
			p2 = sp.Popen(cmd, stdin=p1.stdout, stdout=sp.PIPE)
			p1.stdout.close()
			threading.Thread(target=write_stdin, args=(fi, sr.st_size, p1.stdin, )).start()
			while True:
				buf = p2.stdout.read(512 * 1024)
				if not buf:
					break
				
				fo.write(buf)
			
			for p, name in [[p1, 'xdelta3'], [p2, 'compressor']]:
				p.wait()
				if p.returncode != 0:
					eprint('\n  WARNING:\n    {} returned {}\n'.format(name, p.returncode))
	
	# TODO maybe make this optional
	eprint('verifying patch...')
	p = unpack(fp2)
	for pbuf in apply_patch(ofn):
		sbuf = p.stdout.read(len(pbuf))
		while len(sbuf) < len(pbuf):
			buf2 = p.stdout.read(len(sbuf) - len(pbuf))
			if not buf2:
				eprint('source file truncated?? probably a bug')
				sys.exit(1)
			
			sbuf += buf2
		
		if sbuf != pbuf:
			eprint('ERROR: patch came out bad, pls make an issue')
			sys.exit(1)

	if rm:
		os.remove(fp2)

	eprint('done')


def apply_patch(xdi):
	if not xdi.endswith('.xdi'):
		xdi += '.xdi'
		
	if not os.path.isfile(xdi):
		eprint('file does not exist: {}'.format(xdi))
		sys.exit(1)
	
	ptn = re.compile(r'([0-9]+) ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}) *([0-9]+) *([0-9]+) ([0-9a-f]{40}) ([0-9a-f]{40}) (.*)')
	inf = []
	with open(xdi, 'rb') as f:
		ver = f.readline()
		if ver != b'1\n':
			eprint('got xdi version {}, only support 1'.format(ver))
			sys.exit(1)
		
		for ln in f:
			inf.append(ptn.match(ln.decode('utf-8').rstrip()).groups())
	
	fp1 = inf[0][6]
	fp2 = inf[1][6]
	#sz = getsize(fp1)
	sz = int(inf[1][3])

	env = os.environ.copy()
	env['PATH'] = str('{}:{}'.format(bintmp, env['PATH']))
	p = sp.Popen(['xdelta3', '-dRs', fp1, xdi[:-4]], stdout=sp.PIPE, env=env)
	for buf in speedfilter(p.stdout, sz):
		yield buf
	
	# TODO maybe set lastmod time and chmod


def main():
	if HAVE_PIXZ:
		os.makedirs(bintmp, exist_ok=True)
		xzbin = os.path.join(bintmp, 'xz')
		with open(xzbin, 'wb') as f:
			f.write(b"""#!/bin/bash

[ "$1" =  "-c" ] && exec pixz -7tk
[ "$1" = "-dc" ] && exec pixz -dtk

printf 'bad-args [%s]\n' "$@" >&2
exit 1
""")
		os.chmod(xzbin, 0o755)

	if len(sys.argv) == 2:
		if sys.stdout.isatty():
			eprint('stdout must be redirected to a file, or piped to another process')
			sys.exit(1)
	
		xdi = sys.argv[1]
		for buf in apply_patch(xdi):
			sys.stdout.buffer.write(buf)
		
		return
	
	try:
		fp1, fp2 = sys.argv[1:3]
	except:
		eprint()
		eprint('to create a patch:')
		eprint('  need arg 1: old file')
		eprint('  need arg 2: new file')
		eprint('  optional 3: -rm (remove new)')
		eprint('  (will write to a file)')
		eprint()
		eprint('to apply a patch:')
		eprint('  need arg 1: some.xdi')
		eprint('  (will write to stdout)')
		eprint()
		sys.exit(1)
	
	rm = len(sys.argv) > 3 and sys.argv[3] == '-rm'

	return create_patch(fp1, fp2, rm)

if __name__ == '__main__':
	main()
