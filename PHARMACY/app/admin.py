from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from . import models
from . import views
# Register your models here.
from django.contrib import admin
from .models import UserProfile

admin.site.register(UserProfile)
class CategoryAdmin(admin.ModelAdmin):
    list_display=("name","statusHide")
    list_filter=("name","statusHide")

class  ProductAdmin(admin.ModelAdmin):
    list_display=("name","stock","superbadge","statusHide","noofSales")
    list_filter=("name","stock","superbadge","statusHide","noofSales")

class PrescriptiveCartAdmin(admin.ModelAdmin):
    list_display=("user","product","product_qty","approve")
    list_filter=("user","product","product_qty","approve")
    
class CartAdmin(admin.ModelAdmin):
    model=models.Cart
    list_display=("user","get_name","product_qty")
    list_filter=("user","product","product_qty")

    def get_name(self,obj):
        return obj.product.name
    
    get_name.admin_order_field = 'name'
    get_name.short_description ='product'

class OrderAdmin(admin.ModelAdmin):
    list_display=("orderid","totalprice","totalproducts","status","review")
    list_filter=("orderid","totalprice","totalproducts","status")
    
    

    def get_queryset(self, req):
        qs = super(OrderAdmin, self).get_queryset(req)
        self.req = req
        print(self.req.user.is_superuser)
        if not self.req.user.is_superuser:
            self.exclude=("user","orderid","totalprice","totalproducts","review")
            self.readonly_fields=("orderid",)
        else:
            self.exclude=("",)
            self.readonly_fields=("updated_at",)
        return qs

    


class OrderitemAdmin(admin.ModelAdmin):
    list_display=("get_orderid","quantity","review")
    list_filter=("orderid","quantity","review")
    
    def get_orderid(self,obj):
        return obj.orderid.orderid
    
    get_orderid.admin_order_field = 'name'
    get_orderid.short_description ='Orderid'


class GuestAdmin(admin.ModelAdmin):
    list_display=("guestname","agree","guestid","totalproducts","actualproducts","totalprice","status")
    list_filter=("guestname","agree","guestid","totalproducts","actualproducts","totalprice","status")
    actions = ['send_mail']

    def get_queryset(self, req):
        qs = super(GuestAdmin, self).get_queryset(req)
        self.req = req
        print(self.req.user.is_superuser)
        role=str(self.req.user)
        if not self.req.user.is_superuser and role.replace(" ","") == "deliverypartner":
            print(self.req.user)
            self.exclude=("guestname","agree","guestid","actualproducts","guestPrescriptionImage")
            self.readonly_fields=("guestid","mobileno","email","totalproducts","totalprice")
        else:
            self.exclude=("",)
            self.readonly_fields=("created_at",)
        return qs


    def send_mail(self,req,queryset):
        print(queryset)
        for i in queryset:
            body ="!"
            print(i.email,i.status)
            if i.status == 1:
                host=req.get_host()
                body=f"""Dear {i.guestname} Purchase id:{i.guestid} for {i.totalproducts} products worth Rs.{i.totalprice} is waiting for your conformation
click the link and agree {host}/permit/{i.guestid}
            """

            if i.status == 2: 
                body=f"Dear {i.guestname} Purchase id:{i.guestid} for {i.totalproducts} products worth Rs.{i.totalprice} are Dispatched"

            if i.status == 3: 
                body=f"Dear {i.guestname} Purchase id:{i.guestid} for {i.totalproducts} products worth Rs.{i.totalprice} are Out for delivery"

            if i.status == 4: 
                body=f"Dear {i.guestname} Purchase id:{i.guestid} for {i.totalproducts} products worth Rs.{i.totalprice} are Delivered"

            views.emailhandler(i.email,"Order Updation from Online Pharmacy",body)
            # g=models.Guest.objects.get(id = i)
            # print(queryset[i].values())
class GuestProductsAdmin(admin.ModelAdmin):
    list_display=("get_guestidno","product","quantity","updated")
    list_filter=("product","quantity","updated")
    actions = ['update']
    
    def get_guestidno(self,obj):
        return obj.guestid.guestid
    
    get_guestidno.admin_order_field = 'name'
    get_guestidno.short_description ='Orderid'

    def update(self,req,queryset):
        print(queryset)
        for i in queryset :
            if not i.updated :
                g=models.Guest.objects.get(guestid = i.guestid.guestid)
                g.actualproducts+=1
                g.totalprice+=(models.Product.objects.get(id=i.product.pk ).sellingprice * i.quantity)
                g.save()
                
                print(i.product.pk , i.guestid.guestid)
        queryset.update(updated= True)

class SummaryAdmin(admin.ModelAdmin):
    list_display=("cash","totalcategory","totalproducts","totalsales","guestuser","registered_user")
    
    actions = ['update','view_stat']

    def update(self,req,queryset):
        queryset.update(totalcategory = models.Category.objects.all().count())
        queryset.update(totalproducts = models.Product.objects.all().count())
        queryset.update(totalsales = models.Orders.objects.filter(status = 4).count() + models.Guest.objects.filter(status = 4).count())
        queryset.update(guestuser = models.Guest.objects.all().count())
        queryset.update(registered_user = models.User.objects.all().count())
        ord=models.Orders.objects.filter(status = 4)
        cashflow=0
        for i in ord:
            cashflow += i.totalprice

        guest=models.Guest.objects.filter(status = 4)
        for i in guest:
            cashflow += i.totalprice
        
        queryset.update(cash = cashflow )
        
    def view_stat(self,req,queryset):
        return views.stats(req)


class RefundAdmin(admin.ModelAdmin):
    list_display=("get_orderid","refundAmount","done")
    list_filter=("refundAmount","done")
    readonly_fields=("refundupi",)

    def get_queryset(self, request):
        qs = super(RefundAdmin, self).get_queryset(request)
        self.request = request
        return qs

    def get_orderid(self,obj):
        print(self.request.user.is_superuser)
        return obj.orderid.orderid
    
    get_orderid.admin_order_field = 'name'
    get_orderid.short_description ='Orderid'

# registeration

admin.site.register(models.Product,ProductAdmin)
admin.site.register(models.Category , CategoryAdmin)
admin.site.register(models.Review)
admin.site.register(models.Cart,CartAdmin)
admin.site.register(models.PrescriptiveCart,PrescriptiveCartAdmin)
admin.site.register(models.Orders,OrderAdmin)
admin.site.register(models.Orderitems,OrderitemAdmin)
admin.site.register(models.Refund,RefundAdmin)
admin.site.register(models.Guest,GuestAdmin)
admin.site.register(models.GuestProducts , GuestProductsAdmin)
admin.site.register(models.Summary , SummaryAdmin)
