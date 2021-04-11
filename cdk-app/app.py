#!/usr/bin/env python3
import os

from aws_cdk import core

from cdk_app.cdk_app_stack import CdkAppStack


app = core.App()
CdkAppStack(app, "MyTestStack")

app.synth()
