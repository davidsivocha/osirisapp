# Osiris App #
The Osiris Application is a sales management information system, designed to hold data about Sales Agents and produce performance reports based on the provided data. 

## Languages and Technologies Used ##
- [Python](http://www.python.org/)
- [The Django Framework](https://www.djangoproject.com/)
- HTML5
- Javascript
- [PostgreSQL](http://www.postgresql.org/)
- [Orbit Slider from Zurb](http://www.zurb.com/playground/orbit-jquery-image-slider)
- [Highcharts](http://www.highcharts.com/)
- [JQuery](http://jquery.com/)
- [Tablesorter](http://tablesorter.com/docs/)
- [MaskedInput](http://digitalbush.com/projects/masked-input-plugin/)
- [Django-Admin-Tools](https://bitbucket.org/izi/django-admin-tools/wiki/Home)
- [Django-Admin-Tools-Bootstrap](https://bitbucket.org/salvator/django-admintools-bootstrap)

## About the Project ##
Developed for UK Fuels as a replacement to a spreadsheet driven system that took daily stats input and produced a series of reports, however over time their previous system had become broken and unusable.

This new system is built around the Django framework from Python to fall in line with internal company standards, and to make it easier for their in house team to support.

The system allows for tracking for multiple different teams and agents, and to generate aggregate stats based on performance, as well as use those performance figures to create an in house competition to help drive sales performance.

The system also allows Sales Agents to view their own performance on an intimate level and see in a visually represented for, how well they are doing.

## Modules ##
This section details the module components in Osiris

---------------
### The Academy ###
The academy is a competition system built in, that uses the existing stats to rank the agents by performance and is used to generate monthly and quarterly awards.

### Agents ###
The agents module contains all the details about the sales agents, including sales agent training information.

### Campaigns ###
The Campaigns module manages web sales campaigns to track cost and ROI

### Core ###
The core details the basic function pages, such as index, about, and the login/logout functions

### Extras ###
The extra's module contains some functions that are used in multiple places for consistency. They are little snippets

### Planner ###
The planner is a job recorded for the admin team, for all admin requests.

### Reports ###
The reports module feeds data from the stats module, analyses it and generates reports based on the given data.

### Teams ###
The Teams module is the manager for the teams and the targets that apply to all the agents in that team

### Stats ###
The stats module records the daily stats produced by the agents as well as weekly and monthly stats. All of this data, feeds into the reports and academy modules.