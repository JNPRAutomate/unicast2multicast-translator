# Multicast Menu API

Multicast Menu provides an API to add streams to the site.


## Setup
For the time being, each user of the API must recieve a unique identifier in order to be able to send streams. Contact an admin for one.


## Usage

### Normal Operation
There is one fields that you need for all API operations:
- unique_identifier: Identifies the origination of the request.

For adding streams, you need two additional fields:
- source: IP address of the stream's source
- group: IP address of the stream's group

You can add streams like:
```
requests.post("https://menu.m2icast.net/api/add/", data={"unique_identifier":"<UID>", "source":"<SOURCE_IP>", "group":"<GROUP_IP>"}).content
```

The ".content" at the end is important in order to capture the return value, which is a unique idenfier for the stream that has been added. This access code will be important to delete the stream later.

For removing streams, you only need one additional field:
- access_code: The stream's access code

You can remove streams like:
```
requests.post("https://menu.m2icast.net/api/remove/", data={"unique_identifier":"<UID>", "access_code":"<STREAM_ACCESS_CODE>"}).content
```


### Inside Operation
Multicast Menu actually allows users to upload their own files and have them translated from unicast to multicast using a translation server. If you would like your translation server to be one that Multicast Menu uses to translate these uploaded files, please start by contacting a site admin so that they can mark your translator correctly. Once that has been done, ensure that your code is responding to packets from the Multicast Menu server correctly. You can find sample code for that at [https://github.com/JNPRAutomate/unicast2multicast-translator](https://github.com/JNPRAutomate/unicast2multicast-translator). Generally, ensure that your "inside" API requests look like: 

Adding a Stream:
```
requests.post("https://menu.m2icast.net/api/add/", data={"unique_identifier":"<UID>", "source":"<SOURCE_IP>", "group":"<GROUP_IP>", "inside_request":"True"}).content
```

Removing a Stream:
```
requests.post("https://menu.m2icast.net/api/remove/", data={"unique_identifier":"<UID>", "access_code":"<STREAM_ACCESS_CODE>"}).content
```
