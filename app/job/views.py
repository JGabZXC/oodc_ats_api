from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from core.models import JobPosting
from job.serializers import JobPostingSerializer


# Create your views here.
class JobPostingView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = JobPostingSerializer
    queryset = JobPosting.objects.filter(active=True, published=True)

