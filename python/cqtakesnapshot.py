#!/usr/bin/python

import os,sys,time
from dpapipetools import *
from DPAColors import *
from DPACheesyQNotes import *
from DPACheesyQ import *
from DPACheesyQTasks import *
import re
import DPADataLibrary
import readline

#elapsedTime start machine queueName id noteflag badReturnCodeFlag
namedlineFormat = "%s %s %s %s %s %s"
donelineFormat = "%s %s %s %s %s %s"

timeFilename = DpaPipeCheesyQLocation() + "/fonduetime"

project_path = ".."
seconds_since_epoch = int(time.time())
usage_snapshot_fo = open(project_path + "/ezchz/cq_usage_snapshot_" + str(seconds_since_epoch) + ".ezchz", "w")
tasks_snapshot_fo = open(project_path + "/ezchz/cq_tasks_snapshot_" + str(seconds_since_epoch) + ".ezchz", "w")

def namedBanner(queues, ot,rt,dt,at,nbmach,nbavail):
	banner = ""
	totalWaiting = 0
	totalRunning = 0
	totalDone = 0
	totalArchived = 0
	totalMachines = 0
	totalAvailable  = 0
	for i in range(0,len(queues)):
		q = queues[i]

		status = getOneCheesyQueue(queues[i]).status
		nm = "%s" % str(nbmach[i])
		na = "%s" % str(nbavail[i])
		wait  = "%s" % (str(ot[i]))
		run   = "%s" % (str(rt[i]))
		ndone = "%s" % (str(dt[i]))

		banner = banner + q + ":"
		banner = banner + " " + str(wait) 
		banner = banner + " " + str(run)
		banner = banner + " " + str(ndone)
		banner = banner + " " + str(nm)
		banner = banner + " " + str(na)

		banner = banner + " " + status
		banner = banner + "\n"

		totalWaiting += int(wait)
		totalRunning += int(run)
		totalDone += int(ndone)
		totalMachines += int(nm)
		if status == "running":
			totalAvailable += int(na)

	banner = banner + "Total:" + " " + "%s" % str(totalWaiting) 
	banner = banner + " " + "%s" % str(totalRunning) 
	banner = banner + " " + "%s" % str(totalDone) 
	banner = banner + " " + "%s" % str(totalMachines) 
	banner = banner + " " + "%s" % str(totalAvailable) + "\n"
	return banner



def showNamedItems( items, queueName, status ):
	cqnotes = CheesyQNotes()
	dl = DPADataLibrary.DataFileLibrary(BaseQName)
	for itemid in items:
		task = dl.get(itemid)
		if task != "":
			machine = task.queueMachine
			startTime = task.queueStartTime
			stopTime = task.queueEndTime
			errorCode = ""
			noteflag = ""
			elapsedTime = task.queueElapsedTime

			if cqnotes.noteExists( itemid ):
				noteflag = '*'
			if startTime != "" and stopTime == "":
				elapsedTime = DpaPipeElapsedUnspacedTime( startTime, DpaPipeFormattedUnspacedTime() )
			if startTime != "" and stopTime != "":
				elapsedTime = DpaPipeElapsedUnspacedTime( startTime, stopTime )

			if elapsedTime == "":
				elapsedTime = "null"
			if stopTime == "":
				stopTime = "null"
			if startTime == "":
				startTime = "null"
			snapshotTime = DpaPipeFormattedUnspacedTime()

			if status == "d":
				tasks_snapshot_fo.write( status + " " + donelineFormat % ( itemid, startTime, stopTime, elapsedTime, queueName, snapshotTime ) + "\n" )
			else:
				tasks_snapshot_fo.write( status + " " + namedlineFormat % ( itemid, startTime, elapsedTime, queueName, machine, snapshotTime ) + "\n" )


bannerMessage = ""

usage_snapshot_fo.write( "DPA CHEESYQ USAGE SNAPSHOT\n" + str(seconds_since_epoch) + "\n" )
tasks_snapshot_fo.write( "DPA CHEESYQ TASKS SNAPSHOT\n" + str(seconds_since_epoch) + "\n" )

namedQueues = getCheesyQueuesList()
nbmachines = []
nbavailable = []
nbot = []
nbrt = []
nbdt = []
for queuename in namedQueues:
	nbmachines.append(len(getCheesyQueueMachines(queuename)))
	nbavailable.append(len(getAvailableCheesyQueueMachines(queuename)))

	ot = CheesyQTasks(queuename,"open").showTasks()
	nbot.append( len(ot) )

	stillrunning = CheesyQTasks(queuename,"running").showTasks()
	nbrt.append( len(stillrunning) )

	dt = CheesyQTasks(queuename,"done").showTasks()
	nbdt.append( len(dt) )

	# Waiting tasks
	#ot.sort()
	#showNamedItems( ot, queuename, "w")
	#if len(ot) > 0:
	#	tasks_snapshot_fo.write( "\n" )

	# Running tasks
	stillrunning.sort()
	showNamedItems( stillrunning, queuename, "r")
	if len(stillrunning) > 0:
		tasks_snapshot_fo.write( "\n" )

	#Done tasks
	dt.sort()
	showNamedItems( dt, queuename, "d")
	if len(dt) > 0:
		tasks_snapshot_fo.write( "\n" )

nbat = DPADataLibrary.DataFileLibrary(BaseQName).size()

ban = namedBanner(namedQueues, nbot,nbrt,nbdt,nbat,nbmachines,nbavailable)
usage_snapshot_fo.write( ban )

usage_snapshot_fo.close()
tasks_snapshot_fo.close()
