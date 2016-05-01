#!/usr/bin/env python3

import sys, os, stat, json, requests

def remote_files (rootdir, user, password):
	r = requests.get("https://neocities.org/api/list", auth=(user, password))
	if (r.status_code != 200): quit()
	rjson = json.loads(r.text)
	if (rjson["result"] != "success"): quit()
	return {
		os.path.join(rootdir, entry["path"]): {
			"size": entry["size"] if not entry["is_directory"] else None
		}
		for entry in rjson["files"]
	}

def local_files (rootdir):
	localfiles = dict()
	for root, dirs, files in os.walk(rootdir):
		for f in files:
			if f[0] == ".": continue
			pathname = os.path.join(root, f)
			stats = os.stat(pathname)
			localfiles[pathname] = { "size": stats.st_size if not stat.S_ISDIR(stats.st_mode) else None }
	return localfiles

def comparison (remote, local):
	rset, lset = set(remote), set(local)
	onlyremote = rset.difference(lset)
	onlylocal = lset.difference(rset)
	common = rset.intersection(lset)
	for f in common:
		if remote[f]["size"] != local[f]["size"]:
			if (remote[f]["size"] == None) or (local[f]["size"] == None):
				quit("%s remote and local file types differ." % f)
			else: onlylocal.add(f)
	return onlyremote, onlylocal

def remove_files (rmlist, rootdir, user, password):
	paths = [os.path.relpath(path, rootdir) for path in rmlist]
	r = requests.post(
		"https://neocities.org/api/delete",
		auth=(user, password), 
		data={ "filenames[]": paths }
	)
	print(r.status_code)

def post_files (addlist, rootdir, user, password):
	files = {os.path.relpath(path, rootdir):open(path, "r") for path in addlist}
	r = requests.post(
		"https://neocities.org/api/upload",
		auth=(user, password),
		files=files
	)
	print(r.status_code)

def main():
	rootdir = sys.argv[1] if len(sys.argv) == 2 and sys.argv[1] else "."
	user, password = input("Username: "), input("Password: ")
	rmlist, addlist = comparison(
		remote_files(rootdir, user, password),
		local_files(rootdir))
	if not rmlist: print("No files to delete")
	else: remove_files(rmlist, rootdir, user, password)
	if not addlist: print("No files to upload")
	else: post_files(addlist, rootdir, user, password)

if __name__ == "__main__": main()
