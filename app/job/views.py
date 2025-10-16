from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.permissions import IsHiringManager
from core.models import JobPosting
from job.serializers import JobPostingSerializer
from position.serializers import PositionSerializer
from prf.serializers import PRFSerializer


# Create your views here.
class JobPostingView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = JobPostingSerializer

    def get_queryset(self):
        user = self.request.user
        my_postings = self.request.query_params.get('my_postings', 'false').lower() == 'true'
        no_active = self.request.query_params.get('no_active', 'false').lower() == 'true'
        is_active_param = self.request.query_params.get('is_active', None)
        is_active = True if is_active_param is None else is_active_param.lower() == 'true'
        status = self.request.query_params.get('status', None)
        type = self.request.query_params.get('type', None)

        if user.is_authenticated and my_postings:
            qs = JobPosting.objects.filter(posted_by=user, active=is_active)
            if status:
                qs = qs.filter(status=status)
            if no_active:
                qs = qs.exclude(status='active')
            if type is not None:
                qs = qs.filter(type=type)
            return qs

        return JobPosting.objects.filter(status='active', published=True, active=True)


class JobPostingViewDelete(APIView):
    permission_classes = [IsHiringManager]
    serializer_class = JobPostingSerializer

    def get_queryset(self):
        user = self.request.user
        return JobPosting.objects.filter(posted_by=user)

    def delete(self, request):
        ids = request.data.pop('ids', None)

        if isinstance(ids, list):
            job_postings = self.get_queryset().filter(id__in=ids)
            for job_posting in job_postings:
                serializer = self.serializer_class(job_posting)
                serializer.destroy(serializer.context.get('request', request))
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'error': 'Invalid data. "ids" should be a list of Job Posting IDs.'}, status=status.HTTP_400_BAD_REQUEST)

class JobPostingDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = JobPostingSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            self.permission_classes = [IsHiringManager]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        # user = self.request.user
        # if user.is_authenticated:
        #     return JobPosting.objects.filter(posted_by=user)

        return JobPosting.objects.filter(status='active', published=True, active=True)

    def get(self, request, *args, **kwargs):
        try:
            job_posting_instance = JobPosting.objects.get(id=self.kwargs.get('pk'))
        except JobPosting.DoesNotExist:
            return Response({'error': 'Job Posting not found.'}, status=status.HTTP_404_NOT_FOUND)
        job_posting_data = self.serializer_class(job_posting_instance).data

        type = job_posting_instance.type

        if type == 'prf':
            prf_instance = job_posting_instance.prf
            prf_data = PRFSerializer(prf_instance).data if prf_instance else {}
            data = {**job_posting_data, **prf_data}
        else:
            position_instance = job_posting_instance.position
            position_data = PositionSerializer(position_instance).data if position_instance else {}
            data = {**job_posting_data, **position_data}

        return Response(data, status=status.HTTP_200_OK)


        return super().get(request, *args, **kwargs)

