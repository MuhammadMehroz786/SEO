from django.contrib import admin
from .models import Backlink, BacklinkSnapshot, OutreachProspect, OutreachCampaign, EmailConfig

admin.site.register(Backlink)
admin.site.register(BacklinkSnapshot)
admin.site.register(OutreachProspect)
admin.site.register(OutreachCampaign)
admin.site.register(EmailConfig)
