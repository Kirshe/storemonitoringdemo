from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from storemonitoring.monitoring.models import Report
from storemonitoring.monitoring.serializers import ReportIdSerializer


class TriggerReport(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        report = Report.objects.create()
        ...
        serialized = ReportIdSerializer(instance=report)
        return Response(serialized.data, status=status.HTTP_201_CREATED)


class GetReport(APIView):
    permission_classes = [AllowAny]
    serializer_class = ReportIdSerializer

    def get(self, request):
        serialized = self.serializer_class(data=request.data)
        serialized.is_valid(raise_exception=True)
        report = get_object_or_404(Report, id=serialized.validated_data['report_id'])
        if report.generated:
            return Response(
                data=report.csv,
                status=status.HTTP_200_OK,
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename="report.csv"'
                }
            )
        else:
            return Response({"detail": "report not yet generated"}, status=status.HTTP_425_TOO_EARLY)
