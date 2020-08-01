from setuptools import setup
setup(
	name = 'snapshotalyzer_30000',
	version='0.1',
	author = 'Ke Sun',
	author_email ='kesun@kesun.com',
	description = 'SnapshotAlyzer 30000 uis a tool to manage snapshots',
	license = 'GPLv3+',
	packages = ['shotty'], #the only package/folder in this project
	url = "https://github.com/theprofessor000/snapshotalyzer30000",
	install_requires = [
		'click',
		'boto3'
	],
	entry_points = {
		"console_scripts":[
			"shotty = shotty.shotty:cli"
		]
	}

)