from csv import DictReader
from io import TextIOWrapper
from django.http import HttpResponse

from django.shortcuts import render
from django.views.generic.base import View

from .forms import ImportForm, ProductForm
from .models import Product


class ImportView(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, "import.html", {"form1": ImportForm(), "form": ProductForm()})

    def post(self, request, *args, **kwargs):
        
        row_count = 0
        form_errors = []
        product_uploads = []
        
        if request.method == 'POST' and 'submit' in request.POST:
            formtype = ProductForm
            print(request.POST)
            product = Product.objects.filter(sku=request.POST['sku']).first()
            form = ProductForm(request.POST, instance=product)
            if not form.is_valid():
                form_errors = form.errors
            form.save()
            product_uploads.append(str(Product.objects.filter(sku=request.POST['sku']).first()))
        
        
        if request.method == 'POST' and 'submitmultiple' in request.POST:
            formtype = ImportForm
            try:
                data_file = request.FILES["data_file"] #convert byte stream to a textstream
                rows = TextIOWrapper(data_file, encoding="utf-8", newline="")
            except Exception as e:
                return HttpResponse(f"</b> Error(invlaid file): {e}</b>")
            
            for row in DictReader(rows):
                row_count += 1
                product = Product.objects.filter(sku=row["sku"]).first()
                form = ProductForm(row, instance=product)
                
                if not form.is_valid():
                    form_errors = form.errors
                    break
                
                form.save()
                product_uploads.append(str(Product.objects.filter(sku=row["sku"]).first()))
                
        return render(request, "import.html", {"form": formtype(),
                                            "form_errors": form_errors,
                                            "row_count": row_count,
                                            "product_uploads": product_uploads,
                                            
                        }
                    )
