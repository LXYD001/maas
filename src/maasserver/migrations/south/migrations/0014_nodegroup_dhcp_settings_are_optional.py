# encoding: utf-8
import datetime

from django.db import models
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'NodeGroup.ip_range_high'
        db.alter_column('maasserver_nodegroup', 'ip_range_high', self.gf('django.db.models.fields.IPAddressField')(max_length=15, unique=True, null=True))

        # Changing field 'NodeGroup.broadcast_ip'
        db.alter_column('maasserver_nodegroup', 'broadcast_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True))

        # Changing field 'NodeGroup.ip_range_low'
        db.alter_column('maasserver_nodegroup', 'ip_range_low', self.gf('django.db.models.fields.IPAddressField')(max_length=15, unique=True, null=True))

        # Changing field 'NodeGroup.subnet_mask'
        db.alter_column('maasserver_nodegroup', 'subnet_mask', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True))

        # Changing field 'NodeGroup.router_ip'
        db.alter_column('maasserver_nodegroup', 'router_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True))


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'NodeGroup.ip_range_high'
        raise RuntimeError("Cannot reverse this migration. 'NodeGroup.ip_range_high' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'NodeGroup.broadcast_ip'
        raise RuntimeError("Cannot reverse this migration. 'NodeGroup.broadcast_ip' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'NodeGroup.ip_range_low'
        raise RuntimeError("Cannot reverse this migration. 'NodeGroup.ip_range_low' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'NodeGroup.subnet_mask'
        raise RuntimeError("Cannot reverse this migration. 'NodeGroup.subnet_mask' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'NodeGroup.router_ip'
        raise RuntimeError("Cannot reverse this migration. 'NodeGroup.router_ip' and its values cannot be restored.")


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'maasserver.config': {
            'Meta': {'object_name': 'Config'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('maasserver.fields.JSONObjectField', [], {'null': 'True'})
        },
        'maasserver.dhcplease': {
            'Meta': {'object_name': 'DHCPLease'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'mac': ('maasserver.fields.MACAddressField', [], {}),
            'nodegroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maasserver.NodeGroup']"})
        },
        'maasserver.filestorage': {
            'Meta': {'object_name': 'FileStorage'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'filename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'maasserver.macaddress': {
            'Meta': {'object_name': 'MACAddress'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac_address': ('maasserver.fields.MACAddressField', [], {'unique': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maasserver.Node']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        'maasserver.node': {
            'Meta': {'object_name': 'Node'},
            'after_commissioning_action': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'architecture': ('django.db.models.fields.CharField', [], {'default': "u'i386'", 'max_length': '10'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'error': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'netboot': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'nodegroup': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['maasserver.NodeGroup']", 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'power_parameters': ('maasserver.fields.JSONObjectField', [], {'default': "u''", 'blank': 'True'}),
            'power_type': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '10', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '10'}),
            'system_id': ('django.db.models.fields.CharField', [], {'default': "u'node-07cd231a-cff4-11e1-bbd4-002608dc6120'", 'unique': 'True', 'max_length': '41'}),
            'token': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['piston.Token']", 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        'maasserver.nodegroup': {
            'Meta': {'object_name': 'NodeGroup'},
            'api_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '18'}),
            'api_token': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['piston.Token']", 'unique': 'True'}),
            'broadcast_ip': ('django.db.models.fields.IPAddressField', [], {'default': "u''", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_range_high': ('django.db.models.fields.IPAddressField', [], {'default': "u''", 'max_length': '15', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'ip_range_low': ('django.db.models.fields.IPAddressField', [], {'default': "u''", 'max_length': '15', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'router_ip': ('django.db.models.fields.IPAddressField', [], {'default': "u''", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'subnet_mask': ('django.db.models.fields.IPAddressField', [], {'default': "u''", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'worker_ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'})
        },
        'maasserver.sshkey': {
            'Meta': {'unique_together': "((u'user', u'key'),)", 'object_name': 'SSHKey'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'maasserver.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'piston.consumer': {
            'Meta': {'object_name': 'Consumer'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '16'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'consumers'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'piston.token': {
            'Meta': {'object_name': 'Token'},
            'callback': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'callback_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'consumer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['piston.Consumer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {'default': '1342518254L'}),
            'token_type': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tokens'", 'null': 'True', 'to': "orm['auth.User']"}),
            'verifier': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['maasserver']
