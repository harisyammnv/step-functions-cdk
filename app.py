from aws_cdk import core
from stepfunction.stepfunction_stack import JobPollerStack

app = core.App()
JobPollerStack(app, "aws-stepfunctions-integ2")
app.synth()