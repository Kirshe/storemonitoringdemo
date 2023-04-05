from rest_framework import serializers
from monitoring.models import Report


class ReportIdSerializer(serializers.ModelSerializer):
    report_id = serializers.IntegerField(source='id')

    class Meta:
        model = Report
        fields = ['report_id']