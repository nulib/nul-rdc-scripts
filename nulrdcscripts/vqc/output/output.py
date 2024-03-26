from jinja2 import Template

values = ["clipping","illegal","brng","Exceeds Standards"]
v=0
def videoOutData(errors):
    for i in errors:
            for v in values:
                value = values[v]
                errortype = errors.get("Error Type")


def funneldata(errors):
     pass