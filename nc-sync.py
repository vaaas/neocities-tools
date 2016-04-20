#!/usr/bin/env python3

import sys
import os
import stat
import json
import requests

def calc_root():
	if len(sys.argv) == 2 and sys.argv[1]: return sys.argv[1]
	else: return "."

def get_auth():
	user = input("Username: ")
	password = input("Password: ")
	return user,password

def calc_remote_files (rootdir, user, password):
	r = requests.get("https://neocities.org/api/list", auth=(user, password))
	if (r.status_code != 200): sys.exit(1)
	rjson = json.loads(r.text)
	if (rjson["result"] != "success"): sys.exit(1)
	remotefiles = dict()
	for entry in rjson["files"]:
		pathname = os.path.join(rootdir, entry["path"])
		remotefiles[pathname] = {"is_directory": entry["is_directory"]}
		if not entry["is_directory"]:
			remotefiles[pathname]["size"] = entry["size"]
	return remotefiles

def calc_local_files (rootdir):
	localfiles = dict()
	for root, dirs, files in os.walk(rootdir):
		for f in files:
			if f[0] == ".": continue
			pathname = os.path.join(root, f)
			stats = os.stat(pathname)
			size = stats.st_size
			is_directory = stat.S_ISDIR(stats.st_mode)
			localfiles[pathname] = {"is_directory": is_directory}
			if not is_directory: localfiles[pathname]["size"] = size
	return localfiles

def comparison (remote, local):
	rset = set(remote)
	lset = set(local)
	onlyremote = rset.difference(lset)
	onlylocal = lset.difference(rset)
	common = rset.intersection(lset)
	for f in common:
		if remote[f]["is_directory"] != local[f]["is_directory"]:
			print("%s remote and local file types differ.")
			sys.exit(1)
		elif remote[f]["is_directory"] is False and remote[f]["size"] != local[f]["size"]:
			onlylocal.add(f)
	return onlyremote, onlylocal

def remove_files (rmlist, rootdir, user, password):
	if not rmlist: return print("No files to delete")
	paths = [os.path.relpath(path, rootdir) for path in rmlist]
	r = requests.post(
		"https://neocities.org/api/delete",
		auth=(user, password), 
		data={ "filenames[]": paths }
	)
	print(r.status_code, r.read())

def post_files (addlist, rootdir, user, password):
	if not addlist: return print("No files to upload")
	files = {os.path.relpath(path, rootdir):open(path, "r") for path in addlist}
	r = requests.post(
		"https://neocities.org/api/upload",
		auth=(user, password),
		files=files
	)
	print(r.status_code, r.read())

def main():
	rootdir = calc_root()
	user, password = get_auth()
	remotefiles = calc_remote_files(rootdir, user, password)
	localfiles = calc_local_files(rootdir)
	rmlist, addlist = comparison(remotefiles, localfiles)
	remove_files(rmlist, rootdir, user, password)
	post_files(addlist, rootdir, user, password)

main()
