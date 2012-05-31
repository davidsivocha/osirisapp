from django.db import models

# Create your models here.

# campaign model
# fields:
# campaign name 
# team 
# # of leads bought
# price
# start date
# end date
# campaign notes

# campaign stats model
# fields:
# date
# # of applications

# campaign week stats model
# fields:
# week
# volume

# admin models
# campaign admin
# campaign stats admin
# campaign weekly stats admin


# functions
# price / #ofapps = cost per applications
# #ofapps / #ofleads = percentage return (what percentage of leads signed up.)
# if enddate < today then assert(campaign over) else assert(campaign running)

# forms
# new campaign form
# dailystats form
# weeklystats form

# analytics integration