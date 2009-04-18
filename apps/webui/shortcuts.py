from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage

import csv
import StringIO
import reportlab
import os

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib import colors
from tempfile import mkstemp

pagination_size_default = 20

def as_html(request, template, context):
    return render_to_response(template, 
        context,
        context_instance=RequestContext(request)
        )

def as_pdf(request, objects):
    # this is again some quick and dirty sample code    
    elements = []
    styles = getSampleStyleSheet()
    filename = mkstemp(".pdf")[-1]
    doc = SimpleDocTemplate(filename)

    elements.append(Paragraph("Message Log", styles['Title']))

    data = []
    header = False
    for obj in objects:
        fields = obj._meta.fields
        if not header:
            data.append([f.name for f in fields])
            header = True
        values = [ getattr(obj, f.name) for f in fields ]
        data.append(values)
    
    table = Table(data)
    elements.append(table)
    doc.build(elements)
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=report.pdf'
    response.write(open(filename).read())
    os.remove(filename)
    return response
    
def as_csv(request, objects):
    output = StringIO.StringIO()
    csvio = csv.writer(output)
    header = False
    for obj in objects:
        fields = obj._meta.fields
        if not header:
            csvio.writerow([f.name for f in fields])
            header = True
        values = [ getattr(obj, f.name) for f in fields ]
        csvio.writerow(values)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'    
    response.write(output.getvalue())
    return response

    

def paginate(queryset, number):
    try:
        number = int(number)
    except (TypeError, ValueError):
        # unknown number
        number = 1
        
    pages = Paginator(queryset, pagination_size_default)
    result = { "pages": pages, "count": queryset.count, "jump": jump(pages, number) }
    try:
        result["page"] = pages.page(number)
    except InvalidPage:
        # no page, don't add one in
        pass

    return result
    
def jump(pages, index):
    res = {
        "start_ellipsis": False,
        "end_ellipsis": False
    }

    nums = pages.page_range
    side = 5
    index -= 1
    start = index - side
    if start > 0:
        res["start_ellipsis"] = True
    if start < 0:
        start = 0
    end = index + side + 1
    if end > (len(nums) + 1):
        res["pages_bit"] = nums[start:]
    else:
        res["pages_bit"] = nums[start:end]
        res["end_ellipsis"] = True
    return res
    