import boto3
import botocore
import  sys
import click
session = boto3.Session(profile_name = 'shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
	instances = []
	if project:
		filters = [
					{'Name':'tag:Project',
					'Values':[project]}
				  ]
		instances = ec2.instances.filter(Filters = filters)
		
	else:
		instances = ec2.instances.all()
	return instances

def has_pending_snapshot(volume):
	snapshots = list(volume.snapshots.all())
	return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
	"""Shotty manages snapshots"""
	pass

#group name 'volumes' is the parent command name instead of the funcion defined function name
# @cli.group('XXXXX') def volumes():pass @volumes.command('list') - when using -> shotty.py XXXXX list
@cli.group('volumes') 
def volumes():
	"""Commands for volumes"""
	pass
@volumes.command('list')
@click.option('--project', default=None,help = 'Only volumes for project (tag Project:<name>)')
def list_volumes(project):
	"List Volumes"
	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			print(','.join(
					[v.id,i.id,v.state, str(v.size) +'GiB', v.encrypted and "encrypted" or "not encrypted"]
				))
	return


@cli.group('snapshots')
def snapshots():
	"""Commands for volumes"""
	pass

@snapshots.command('list')
@click.option('--project',default=None,help='Only snapshots for project (tag Project:<name>)')
# option '--all', if '--all' is present, then list_all turns to True from default value-False
@click.option('--all', 'list_all', default=False, is_flag= True,
	help = "List all snapshots fir each volume, not just the most recent one")
def list_snapshots(project, list_all):
	"List EC2 snapshots"
	instances = filter_instances(project)
	for i in instances:
		for v in i.volumes.all():
			for s in v.snapshots.all():
				# aws give snapshot in time descending order - most recent one first
				print(', '.join(
						[s.id, v.id, i.id, s.state, s.progress, s.start_time.strftime("%c")]
					))
				if s.state == 'completed' and not list_all:break
	return

@cli.group('instances')
def instances():
	"""Commands for instances"""
	pass

@instances.command('snapshot', help = 'Create snapshots of all volumes')
@click.option('--project', default=None, help = 'Only instances for project (tag Project:<name>)')
def create_snapshots(project):
	instances = filter_instances(project)
	for i in instances:
		print("Stopping {0}".format(i.id))
		i.stop()
		i.wait_until_stopped()
		for v in i.volumes.all():
			if has_pending_snapshot(v):
				print("Skipping {0}, snapshot is already in progress".format(v.id))
			print('Creating snapshots of {0}'.format(v.id))
			v.create_snapshot(Description = 'Created by SnapshotAlyzer 30000')
		print("Start {0}".format((i.id)))
		i.start()
		i.wait_until_running()
	print("Job is done!")
	return

#work as instances' subcomand
#click.command(name=None, cls=None, **attrs)
@instances.command('list')
@click.option('--project', default=None,help = 'Only instances for project (tag Project:<name>)')
def list_instances(project):
	#click use doc for the help messages
	"List EC2 instances"
	instances = filter_instances(project)

	for i in instances:
		my_tags = {t['Key']:t['Value'] for t in i.tags or []}
		print(
			','.join((i.id,i.instance_type, i.placement['AvailabilityZone'],
			i.state['Name'],i.public_dns_name)),
			my_tags.get('Project','<no project>')
			)
	
	return

@instances.command('stop')
@click.option('--project', default=None, help='Only instances for project')
def stop_instances(project):
	"Stop EC2 instances"
	instances = filter_instances(project)

	for i in instances:
		print("Stopping {0}...".format(i.id))
		try:
			i.stop()
		except botocore.exceptions.ClientError as e:
			print("Can't stop {0} due to ".format(i.id),str(e))
			continue
	return

@instances.command('start')
@click.option('--project', default=None, help='Only instances for project')
def start_instances(project):
	"Start EC2 instances"
	instances = filter_instances(project)

	for i in instances:
		print("Starting {0}...".format(i.id))
		try:
			i.start()
		except botocore.exceptions.ClientError as e:
			print("Can't start {0} due to ".format(i.id),str(e))
			continue
	return

if __name__ =='__main__':
	#print(sys.argv)
	cli()
	
