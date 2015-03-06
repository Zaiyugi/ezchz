#!/usr/bin/python

import os, sys, re

project_path = ".."
web_path = "../html/queue_data"

data_in = "/total_done_tasks"
xml_out = data_in + ".xml"
indent = "   "

def parseTime(s):
	calendar = s[:10]
	hours = s[11:13]
	minutes = s[14:16]
	seconds = s[17:19]
	return calendar + " " + hours + ":" + minutes + ":" + seconds


data_fos = open(project_path+data_in, "r")
xml_fos = open(web_path+xml_out, "w")

xml_fos.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
xml_fos.write("<TaskListing>\n");

level = 1
for line in data_fos:
	task_info = line.split();

	taskId = task_info[0];
	taskStarted = task_info[1];
	taskFinished = task_info[2];
	taskElapsed = task_info[3];
	taskQueue = task_info[4];
	snapshotTime = task_info[5];

	# Parse taskId using regex for additional info
	searchStr = taskId
	match = re.search(r'^[a-z]*', searchStr)
	taskUser = match.group()

	searchStr = searchStr[match.end():]
	match = re.search(r'[0-9]*$', searchStr)
	frame = match.group()

	searchStr = searchStr[:match.start()]
	match = re.search(r'^[0-9_\-]*', searchStr)
	taskSubmitted = match.group()

	searchStr = searchStr[match.end():]
	match = re.search(r'^share|^s(hot)?[0-9]*', searchStr)
	if match:
		shot = match.group()
		searchStr = searchStr[match.end():]
	else:
		shot = "None"

	job = searchStr

	xml_fos.write(level*indent + "<Task>\n");
	level += 1

	xml_fos.write(level*indent + "<user>" + taskUser + "</user>\n");
	xml_fos.write(level*indent + "<shot>" + shot + "</shot>\n");
	xml_fos.write(level*indent + "<task>" + job + "</task>\n");
	xml_fos.write(level*indent + "<frame>" + frame + "</frame>\n");
	xml_fos.write(level*indent + "<submit>" + parseTime(taskSubmitted) + "</submit>\n");
	xml_fos.write(level*indent + "<start>" + parseTime(taskStarted) + "</start>\n");
	xml_fos.write(level*indent + "<finish>" + parseTime(taskFinished) + "</finish>\n");
	xml_fos.write(level*indent + "<elapsed>" + taskElapsed + "</elapsed>\n");
	xml_fos.write(level*indent + "<queue>" + taskQueue + "</queue>\n");
	xml_fos.write(level*indent + "<ss_taken>" + parseTime(snapshotTime) + "</ss_taken>\n");
	xml_fos.write(level*indent + "<qtask_id>" + task_info[0] + "</qtask_id>\n");

	level -= 1
	xml_fos.write(level*indent + "</Task>\n");

xml_fos.write("</TaskListing>\n");

data_fos.close();
xml_fos.close();
