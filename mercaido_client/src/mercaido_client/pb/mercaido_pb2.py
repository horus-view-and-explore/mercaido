# SPDX-FileCopyrightText: 2023, 2024 Horus View and Explore B.V.
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mercaido.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0emercaido.proto\x12\x0ehorus.mercaido\"~\n\x0bMessageBase\x12\x11\n\trecipient\x18\x01 \x01(\t\x12,\n\x07request\x18\x02 \x01(\x0b\x32\x1b.horus.mercaido.RequestBase\x12.\n\x08response\x18\x03 \x01(\x0b\x32\x1c.horus.mercaido.ResponseBase\"\xcc\x01\n\x0bRequestBase\x12)\n\x04type\x18\x02 \x01(\x0e\x32\x1b.horus.mercaido.MessageType\x12;\n\x11register_services\x18\x03 \x01(\x0b\x32 .horus.mercaido.RegisterServices\x12/\n\x0bpublish_job\x18\x04 \x01(\x0b\x32\x1a.horus.mercaido.PublishJob\x12$\n\x05\x65vent\x18\x05 \x01(\x0b\x32\x15.horus.mercaido.Event\"J\n\x0cResponseBase\x12)\n\x04type\x18\x02 \x01(\x0e\x32\x1b.horus.mercaido.MessageType\x12\x0f\n\x07success\x18\x03 \x01(\x08\"z\n\x07Service\x12\x10\n\x08\x65ndpoint\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12-\n\nattributes\x18\x04 \x03(\x0b\x32\x19.horus.mercaido.Attribute\x12\x0b\n\x03svg\x18\x05 \x01(\t\"=\n\x10RegisterServices\x12)\n\x08services\x18\x01 \x03(\x0b\x32\x17.horus.mercaido.Service\"G\n\nPublishJob\x12)\n\x08services\x18\x01 \x03(\x0b\x32\x17.horus.mercaido.Service\x12\x0e\n\x06job_id\x18\x02 \x02(\t\"\x9a\x01\n\tAttribute\x12+\n\x04type\x18\x01 \x02(\x0e\x32\x1d.horus.mercaido.AttributeType\x12\x14\n\x0c\x64isplay_name\x18\x02 \x01(\t\x12\x1b\n\x13\x64isplay_description\x18\x03 \x01(\t\x12\x0e\n\x06values\x18\x04 \x03(\t\x12\n\n\x02id\x18\x05 \x01(\t\x12\x11\n\tsensitive\x18\x06 \x01(\x08\"i\n\x05\x45vent\x12\'\n\x04type\x18\x01 \x02(\x0e\x32\x19.horus.mercaido.EventType\x12\x0e\n\x06job_id\x18\x02 \x01(\t\x12\x10\n\x08progress\x18\x03 \x01(\x01\x12\x15\n\rerror_message\x18\x04 \x01(\t*\x85\x01\n\x0bMessageType\x12\x1c\n\x18MESSAGE_TYPE_UNSPECIFIED\x10\x00\x12\x16\n\x12MESSAGE_TYPE_EVENT\x10\x02\x12\"\n\x1eMESSAGE_TYPE_REGISTER_SERVICES\x10\x03\x12\x1c\n\x18MESSAGE_TYPE_PUBLISH_JOB\x10\x04*\xcf\x02\n\rAttributeType\x12\x1e\n\x1a\x41TTRIBUTE_TYPE_UNSPECIFIED\x10\x00\x12\x17\n\x13\x41TTRIBUTE_TYPE_TEXT\x10\x01\x12\x17\n\x13\x41TTRIBUTE_TYPE_FILE\x10\x02\x12\x19\n\x15\x41TTRIBUTE_TYPE_FOLDER\x10\x03\x12\x1c\n\x18\x41TTRIBUTE_TYPE_SELECTION\x10\x04\x12\x1f\n\x1b\x41TTRIBUTE_TYPE_RECORDING_ID\x10\x05\x12/\n+ATTRIBUTE_TYPE_RECORDINGS_SERVER_CONNECTION\x10\x06\x12*\n&ATTRIBUTE_TYPE_MEDIA_SERVER_CONNECTION\x10\x07\x12\x19\n\x15\x41TTRIBUTE_TYPE_NUMBER\x10\x08\x12\x1a\n\x16\x41TTRIBUTE_TYPE_BOOLEAN\x10\t*\x91\x01\n\tEventType\x12\x1a\n\x16\x45VENT_TYPE_UNSPECIFIED\x10\x00\x12\x18\n\x14\x45VENT_TYPE_JOB_START\x10\x01\x12\x17\n\x13\x45VENT_TYPE_JOB_STOP\x10\x02\x12\x18\n\x14\x45VENT_TYPE_JOB_ERROR\x10\x03\x12\x1b\n\x17\x45VENT_TYPE_JOB_PROGRESS\x10\x04')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mercaido_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MESSAGETYPE']._serialized_start=970
  _globals['_MESSAGETYPE']._serialized_end=1103
  _globals['_ATTRIBUTETYPE']._serialized_start=1106
  _globals['_ATTRIBUTETYPE']._serialized_end=1441
  _globals['_EVENTTYPE']._serialized_start=1444
  _globals['_EVENTTYPE']._serialized_end=1589
  _globals['_MESSAGEBASE']._serialized_start=34
  _globals['_MESSAGEBASE']._serialized_end=160
  _globals['_REQUESTBASE']._serialized_start=163
  _globals['_REQUESTBASE']._serialized_end=367
  _globals['_RESPONSEBASE']._serialized_start=369
  _globals['_RESPONSEBASE']._serialized_end=443
  _globals['_SERVICE']._serialized_start=445
  _globals['_SERVICE']._serialized_end=567
  _globals['_REGISTERSERVICES']._serialized_start=569
  _globals['_REGISTERSERVICES']._serialized_end=630
  _globals['_PUBLISHJOB']._serialized_start=632
  _globals['_PUBLISHJOB']._serialized_end=703
  _globals['_ATTRIBUTE']._serialized_start=706
  _globals['_ATTRIBUTE']._serialized_end=860
  _globals['_EVENT']._serialized_start=862
  _globals['_EVENT']._serialized_end=967
# @@protoc_insertion_point(module_scope)