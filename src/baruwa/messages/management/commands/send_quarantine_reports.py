# 
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010  Andrew Colin Kissa <andrew@topdog.za.net>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# vim: ai ts=4 sts=4 et sw=4
#

from django.core.management.base import NoArgsCommand

def generate_release_records(query_list):
    """
    Creates the DB records to be lookedup by the release
    mechanisim
    """
    for record in query_list:
        try:
            if not email_re.match(user.email):
                release_address = user.username
            else:
                release_address = user.email
            r = Release(uuid=record['uuid'],timestamp=record['timestamp'],message_id=record['id'],
            release_address=release_address)
            r.save()
        except:
            pass
 
def add_uuids(query_list):
    """
    Adds uuids to the queryset for using in the template
    """
    import uuid
     
    for index, msg in enumerate(query_list):
        query_list[index]['uuid'] = str(uuid.uuid5(uuid.NAMESPACE_OID, str(msg['id'])))  
    
class Command(NoArgsCommand):
    help = "Generates an email report of the quarantined messages for the past 24 hours"

    def handle_noargs(self, **options):
        from django.template.loader import render_to_string
        from django.contrib.auth.models import User
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        from baruwa.messages.models import Message, Release
        from baruwa.accounts.models import UserProfile
        import datetime
        try:
            from django.forms.fields import email_re
        except ImportError:
            from django.core.validators import email_re


        tmp = UserProfile.objects.values('user').filter(send_report=1)
        ids = [ id['user'] for id in tmp ]
        users = User.objects.filter(id__in=ids)
        url = getattr(settings, 'QUARANTINE_REPORT_HOSTURL','')
        a_day = datetime.timedelta(days=1)
        yesterday = datetime.date.today() - a_day
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL','postmaster@localhost')
        print "=================== Processing quarantine notifications ======================"
        for user in users:
            if email_re.match(user.email) or email_re.match(user.username):
                spam_list = Message.quarantine_report.for_user(user).values('id','timestamp','from_address',
                    'to_address','subject').exclude(timestamp__lt=yesterday).exclude(spam=0).order_by('sascore')[:25]
                policy_list = Message.quarantine_report.for_user(user).values('id','timestamp','from_address',
                    'to_address','subject').exclude(timestamp__lt=yesterday).exclude(spam=1).order_by('sascore')[:25]
                subject = 'Baruwa quarantine report for %s' % user.username
                
                if email_re.match(user.username):
                    to = user.username
                if email_re.match(user.email):
                    to = user.email

                if spam_list or policy_list:
                    for query_list in [spam_list, policy_list]:
                        add_uuids(query_list)
                        
                    html_content = render_to_string('messages/quarantine_report.html',
                        {'spam_items':spam_list, 'policy_items':policy_list, 'host_url':url})
                    text_content = render_to_string('messages/quarantine_report_text.html',
                        {'spam_items':spam_list, 'policy_items':policy_list, 'host_url':url})
                        
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    for query_list in [spam_list, policy_list]:
                        generate_release_records(query_list)

                    print "sent quarantine report to "+to
                else:
                    print "skipping report to "+to+" no messages"
        print "=================== completed quarantine notifications ======================"
