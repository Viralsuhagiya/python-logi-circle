# -*- coding: utf-8 -*-
"""The tests for the Logi API platform."""
import json
from unittest.mock import MagicMock
from datetime import datetime
import pytz
from tests.test_base import LogiUnitTestBase
from logi_circle.activity import Activity
from logi_circle.const import (API_BASE,
                               ISO8601_FORMAT_MASK,
                               ACCEPT_IMAGE_HEADER,
                               ACCEPT_VIDEO_HEADER,
                               ACTIVITY_IMAGE_ENDPOINT,
                               ACTIVITY_MP4_ENDPOINT,
                               ACTIVITY_DASH_ENDPOINT,
                               ACTIVITY_HLS_ENDPOINT)
from .helpers import async_return

BASE_ACTIVITY_URL = '/abc123'
TEST_TZ = 'Etc/GMT+10'


class TestActivity(LogiUnitTestBase):
    """Unit test for the Activity class."""

    def setUp(self):
        """Set up Activity class with fixtures"""
        super(TestActivity, self).setUp()

        self.activity_json = json.loads(self.fixtures['activity'])
        self.activity = Activity(activity=self.activity_json,
                                 logi=self.logi,
                                 url=BASE_ACTIVITY_URL,
                                 local_tz=pytz.timezone(TEST_TZ))

    def tearDown(self):
        """Remove test Activity instance"""
        super(TestActivity, self).tearDown()
        del self.activity_json
        del self.activity

    def test_activity_props(self):
        """Test props match fixture"""
        self.assertEqual(self.activity.activity_id, self.activity_json['activityId'])
        self.assertEqual(self.activity.duration.seconds, self.activity_json['playbackDuration'] / 1000)
        self.assertEqual(self.activity.start_time_utc,
                         datetime.strptime(self.activity_json['startTime'], ISO8601_FORMAT_MASK))
        self.assertEqual(self.activity.end_time_utc,
                         datetime.strptime(self.activity_json['endTime'], ISO8601_FORMAT_MASK))
        self.assertEqual(self.activity.start_time,
                         self.activity.start_time_utc.replace(
                             tzinfo=pytz.utc).astimezone(self.activity._local_tz))
        self.assertEqual(self.activity.end_time,
                         self.activity.end_time_utc.replace(
                             tzinfo=pytz.utc).astimezone(self.activity._local_tz))

    def test_activity_assets(self):
        """Test props match fixture"""
        url_base = '%s%s/%s' % (API_BASE, BASE_ACTIVITY_URL, self.activity_json['activityId'])
        self.assertEqual(self.activity.jpeg_url, url_base + ACTIVITY_IMAGE_ENDPOINT)
        self.assertEqual(self.activity.mp4_url, url_base + ACTIVITY_MP4_ENDPOINT)
        self.assertEqual(self.activity.hls_url, url_base + ACTIVITY_HLS_ENDPOINT)
        self.assertEqual(self.activity.dash_url, url_base + ACTIVITY_DASH_ENDPOINT)

        my_file = 'myfile.file'

        self.activity._get_file = MagicMock(
            return_value=async_return(None))

        async def run_test():
            # Image
            await self.activity.download_jpeg(my_file)
            self.activity._get_file.assert_called_with(url=self.activity.jpeg_url,
                                                       filename=my_file,
                                                       accept_header=ACCEPT_IMAGE_HEADER)

            # Video
            await self.activity.download_mp4(my_file)
            self.activity._get_file.assert_called_with(url=self.activity.mp4_url,
                                                       filename=my_file,
                                                       accept_header=ACCEPT_VIDEO_HEADER)

            # Dash
            await self.activity.download_dash(my_file)
            self.activity._get_file.assert_called_with(url=self.activity.dash_url,
                                                       filename=my_file)

            # HLS
            await self.activity.download_hls(my_file)
            self.activity._get_file.assert_called_with(url=self.activity.hls_url,
                                                       filename=my_file)

        self.loop.run_until_complete(run_test())
