from rest_framework import generics, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address

from ...utils import create_random_string
from ..view.models import Stream
from .models import APISubmission, Translator, UploadSubmission
from .serializers import AddSerializer, RemoveSerializer


class SubmissionAdd(generics.CreateAPIView):
    serializer_class = AddSerializer

    def create(self, request):
        source = request.data.get("source")
        group = request.data.get("group")
        unique_identifier = request.data.get("unique_identifier")
        inside_request = bool(request.data.get("inside_request"))

        if not source or not group or not unique_identifier:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                translation_server = Translator.objects.get(uid=unique_identifier)
            except:
                return Response({"error": "Invalid translation server unique identifier"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Validate
                try:
                    validate_ipv4_address(source)
                    validate_ipv4_address(group)
                except ValidationError:
                    return Response({"error": "Invalid source or group specified."}, status=status.HTTP_400_BAD_REQUEST)
                if Stream.objects.filter(source=source, group=group).exists():
                    return Response({"error": "This stream already exists. Contact an admin to claim it."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Handle
                if inside_request:
                    if not translation_server.allowed_inside:
                        return Response({"error": "This translation server cannot make inside requests."}, status=status.HTTP_400_BAD_REQUEST)
                    # TODO: Find better way to match streams
                    unmatched = UploadSubmission.objects.filter(matched=False).order_by("time")
                    if unmatched.exists():
                        submission = unmatched[0]
                        stream = submission.stream
                        stream.source = source
                        stream.group = group
                        stream.active = True
                        stream.save()
                        submission.matched = True
                        submission.save()
                        return Response({"data": "Your access code for claiming, editing or deleting the string is {}".format(submission.access_code)}, status=status.HTTP_201_CREATED)
                    else:
                        access_code = create_random_string(40)
                        api_user = get_user_model().objects.get_or_create(
                            username="API"
                        )[0]
                        stream = Stream.objects.create(
                            owner=api_user,
                            collection_method="04",
                            source=source,
                            group=group,
                            source_name=translation_server.name,
                        )
                        APISubmission.objects.create(
                            stream=stream,
                            translator=translation_server,
                            access_code=access_code,
                        )
                        return Response({"data": "Your access code for claiming, editing or deleting the string is {}".format(access_code)}, status=status.HTTP_201_CREATED)
                else:
                    access_code = create_random_string(40)
                    api_user = get_user_model().objects.get_or_create(
                        username="API"
                    )[0]
                    stream = Stream.objects.create(
                        owner=api_user,
                        collection_method="04",
                        source=source,
                        group=group,
                        source_name=translation_server.name,
                    )
                    APISubmission.objects.create(
                        stream=stream,
                        translator=translation_server,
                        access_code=access_code,
                    )

                    return Response({"data": "Your access code for claiming, editing or deleting the string is {}".format(access_code)}, status=status.HTTP_201_CREATED)


class SubmissionRemove(generics.CreateAPIView):
    serializer_class = RemoveSerializer

    def create(self, request):
        unique_identifier = request.data.get("unique_identifier")
        access_code = request.data.get("access_code")
        submission = None

        if not unique_identifier or not access_code:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                Translator.objects.get(uid=unique_identifier)
            except:
                return Response({"error": "Invalid translation server unique identifier"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                submission = None
                try:
                    submission = APISubmission.objects.get(access_code=access_code)
                except:
                    try:
                        submission = UploadSubmission.objects.get(access_code=access_code)
                    except:
                        return Response({"error": "Invalid submission access code."}, status=status.HTTP_400_BAD_REQUEST)
                
                stream = submission.stream
                submission.delete()
                stream.delete()

                return Response({"data": "Your stream has been deleted."}, status=status.HTTP_201_CREATED)    
