from collections import UserDict
from sys import setprofile
from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from .models import *
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import random
from email.message import  EmailMessage
from email.mime.text import MIMEText
import ssl
import smtplib
import razorpay
from django.utils.crypto import get_random_string
from datetime import datetime



otp=random.randint(100000,999999)


def emailhandler(email,subject,msg):
    sender = "chinnakotlasreeharsha6272@gmail.com"
    password = "lfpk oawl lfnf qozy"
    receiver = email
    em=EmailMessage()
    em['From'] = sender
    em['To'] = receiver
    em['subject'] = subject
    em.set_content(msg)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(sender,password)
        smtp.sendmail(sender,receiver,em.as_string())
    print("sent successfully -----------------------", otp)
    print("success")

    
# send otp to the entererd mail
def sendmail(otp,email):
    sender = "chinnakotlasreeharsha6272@gmail.com"
    password = "lfpk oawl lfnf qozy"
    receiver = email
    # receiver=input("enter email id")
    subject = "OTP for Online Pharmacy"
    body = f"""<#> {otp} is your Online Pharmacy verification code"""
    em=EmailMessage()
    em['From'] = sender
    em['To'] = receiver
    em['subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(sender,password)
        smtp.sendmail(sender,receiver,em.as_string())
    print("sent successfully", otp)


def resetpassword(req,email,code):
    try:
        user=User.objects.get(username=email)
        token=str(user.last_login)[:10]
        if req.method =="POST":
            pw=req.POST['password']
            user.set_password(pw)
            user.save()
            userlogin(req,user.username,pw)
            print("pw changed to",pw)
            return render(req,"message.html",{"msg" :"password successfully changed"})
        if(email == user.username and code==token):
            return render(req,'getconfirm.html')
        else:
            return render(req,"message.html",{"msg" :"Link Has Expired try again"})
    except :
        return render(req,"message.html",{"msg" :"Invalid Link"})


# return HttpResponse(email + code+" "+user.username+token)
def getmail(req):
    if req.method == "POST":
        mail=req.POST['mail']
        print(mail)
        try :
            user=User.objects.get(username=mail)
            token=str(user.last_login)[:10]
            print(user.last_login)
            host=req.get_host()
            sub="Password Recovery"
            body=f""" click the below link to reset the Password,Valid for 24 hrs
            {host}/forgot/{mail}/{token}     """
            emailhandler(mail,sub,body)
            return render(req,"message.html",{"msg" :"Email send successfull please check your Email "})
        except:
            return render(req,'getmail.html',{"err":"Email doesn't exist please Register"})
    return render(req,'getmail.html')


def userlogin(req,username,password):
    try:
        logout(req)   
    finally:
        user=authenticate(req, username =username , password =password)
        if user is not None:
            login(req,user)
            print("user loged in")
            return True
        else:
            print("user not valid")
            return False
  
    
def makeuserlogin(req):
    if req.method =="POST":
        uname=req.POST['loginmail']
        upass=req.POST['loginpass']
        if userlogin(req,uname,upass) :
            return redirect("/")
        else:
            return render(req,"login.html",{"err":"Invalid Login credentials"})
    return redirect('/loginpage/')


def shop(req):
        try:
            category=Category.objects.filter(statusHide=1)
            products=Product.objects.exclude(statusHide=1)
            products=Product.objects.exclude(category_type__statusHide=1)                      
            if 'q' in req.GET:
                q=req.GET['q']
                print(q,"-------------------------------------")
                multipleQ=Q(Q(name__icontains=q) | Q(purpose__icontains=q) | Q(description__icontains=q)  | Q(superbadge__icontains=q) | Q(ratings__icontains=q) | Q(sellingprice__icontains=q) )
                products=products.filter(multipleQ)
            category=Category.objects.filter(statusHide=0)
            return render(req,'shop.html',{"products":products,"category":category })  
        except: 
            print("here")
            products=Product.objects.filter(statusHide=0)
            category=Category.objects.filter(statusHide=0)
            return render(req,'shop.html',{"products":products,"category":category})    


def shopcategory(req,name):
    no=int(name)
    if(Category.objects.filter(id=no ,statusHide=0)):
        category=Category.objects.filter(statusHide=0)
        cattype=Category.objects.get(id=no)
        if(Product.objects.filter(category_type=no)):
            products=Product.objects.filter(category_type=no).filter(statusHide=0)            
            return render(req,'shop.html',{"products":products,"cattype":cattype,"category" :category}) 
        else:
            messages.warning(req,"No such category")
            return redirect('shop')
    else:
        messages.warning(req,"No such category")
        return redirect('shop')


def updatecart(req,str,productid,cartid):
    cart=Cart.objects.filter(user=req.user).get(product_id=productid)
    product=Product.objects.get(id=productid)
    productstock=product.stock
    if cart:
        cartqty=cart.product_qty
        if str== "add" and productstock > cartqty:
            cart.product_qty=cartqty+1
            cart.save()
            print("add")
        elif str== "sub" and cartqty > 1:
            cart.product_qty=cartqty-1
            cart.save()
            print("sub")
        elif str =="del" or (str =="sub" and cartqty):
            Cart.objects.get(id=cartid).delete()           
            print("delete")
    return redirect("cart")
 

def cartview(req):
    if req.user.is_authenticated :
        user=req.user
        cart=Cart.objects.all().filter(user=user)
        count=cart.count()
        print(count)
        PrescriptiveProduct=PrescriptiveCart.objects.filter(user=user)
        pp=len(PrescriptiveProduct)
        print(PrescriptiveProduct,pp)
        totalAmt=0
        for i in cart:
            totalAmt +=i.product.sellingprice * i.product_qty
        return render(req,"cart.html",{"cart":cart,"count":count,"totalAmt":totalAmt,"PrescriptiveProduct" : PrescriptiveProduct,"pp":pp})
    return render(req,"cart.html")


def addToCart(req):
    if req.user.is_authenticated :
        if req.method=="POST" and not Cart.objects.filter(user=req.user,product=req.POST['id']):            
                cart=Cart()
                cart.user=req.user
                cart.product=Product.objects.get(id=req.POST['id'])
                cart.product_qty=req.POST['quantity']
                cart.save()
                print(Cart.objects.filter(user=req.user).filter(product=req.POST['id']))
                return redirect('cart')
        return redirect('cart')
    return redirect('cart')


def delTemperary(req,id):
    PrescriptiveCart.objects.get(id=id).delete()
    return redirect('cart')
    

def addtotop(req,id):
    if req.user.is_authenticated :
        if not Cart.objects.filter(user=req.user,product=PrescriptiveCart.objects.get(id=id).product):
                Prescriptive= PrescriptiveCart.objects.get(id=id)
                cart=Cart()
                cart.user=req.user
                cart.product=Prescriptive.product
                cart.product_qty=Prescriptive.product_qty
                cart.save()
                PrescriptiveCart.objects.get(id=id).delete()
                return redirect('cart')
        return redirect('cart')
    return redirect('cart')


'''def approveCart(req):
    cart=PrescriptiveCart()
    if req.method == "POST":
        if not (PrescriptiveCart.objects.filter(user=req.user,product=req.POST['id'])):
            cart.user=req.user
            cart.PrescriptionImage=req.FILES.get("image")
            cart.product=Product.objects.get(id=req.POST['id'])
            cart.product_qty=req.POST['quantity']
            cart.approve="Processing"
            cart.save()
        return redirect("cart")   
    return redirect("cart")'''
    
    
from django.core.files.uploadhandler import FileUploadHandler  # Import the FileUploadHandler
from django.core.exceptions import SuspiciousFileOperation  # Import SuspiciousFileOperation for file size validation
from django.conf import settings  # Import settings for maximum file size

def approveCart(req):
    cart = PrescriptiveCart()
    
    if req.method == "POST":
        # Check if the uploaded file is a PDF
        uploaded_file = req.FILES.get("image")
        if uploaded_file:
            if not uploaded_file.name.endswith(".pdf"):
                # Handle non-PDF file uploads here, e.g., show an error message
                return redirect("cart")
            
            # Check if the file size is less than 5MB
            if uploaded_file.size > settings.MAX_PDF_FILE_SIZE:
                # Handle large file uploads here, e.g., show an error message
                return redirect("cart")

        if not (PrescriptiveCart.objects.filter(user=req.user, product=req.POST['id'])):
            cart.user = req.user
            cart.PrescriptionImage = uploaded_file  # Assign the uploaded PDF file
            cart.product = Product.objects.get(id=req.POST['id'])
            cart.product_qty = req.POST['quantity']
            cart.approve = "Processing"
            cart.save()
        
        return redirect("cart")
    
    return redirect("cart")



def productview(req,id):    
    try :
        items = list(Product.objects.exclude(id=id).filter(category_type=Product.objects.get(id=id).category_type))
        # for random product 
        n=3
        if len(items)<3:
            n=len(items)
        random_items = random.sample(items, n)
        print(random_items)
        product=Product.objects.get(id=id)
        reviews=Review.objects.all().filter(product_name=id)
        if not reviews:
            return render(req,'product.html',{"product":product,"similar":random_items})
        return render(req,'product.html',{"product":product,"similar":random_items,"reviews":reviews})
    except :
        print("no")
        return render(req,'product.html',{"err":"No Such Product Exist"})


def home(req):    
    category=Category.objects.filter(statusHide=0)
    return render(req,"landing.html",{"category" :category})


def loginpage(req):
    return render(req,"login.html")


def registerationpage(req):
    return render(req,"registration.html")


'''def sendverifyotp(req):
    if req.method == "POST":
        otp1=req.POST['otp']
        if otp == int(otp1):
            newuser=User.objects.create_user(req.session["email"],req.session["email"],req.session["password"])
            newuser.first_name=req.session["name"]
            newuser.last_name=req.session["contactno"]
            newuser.save()
            userlogin(req,req.session["email"],req.session["password"])
            return render(req,'landing.html')   
        else:
            return render(req,'otp.html',{"err":"Invalid OTP!!!"})
    print("success "+ req.session["email"])
    return render(req,'otp.html')


def register(req):
    if req.method =="POST":
        email=req.POST['email']
        name=req.POST['name']
        date_of_birth = req.POST['date_of_birth']
        contactno=req.POST['contactno']
        password=req.POST['psw']
        req.session["email"]=email
        req.session["name"]=name
        req.session["contactno"]=contactno
        req.session["password"]=password
        try :
            user=User.objects.get(username=email)
            print(user)
            print(email,name,date_of_birth,contactno,password)           
            return render(req,"login.html",{"err":"User already exist please login"})
        except :
            global otp 
            otp= random.randint(100000,999999)
            sendmail(otp,email)
            return render(req,'otp.html')'''
            
def sendverifyotp(req):
    if req.method == "POST":
        otp1=req.POST['otp']
        if otp == int(otp1):
            email = req.session["email"]
            name = req.session["name"]
            dob = req.session["dob"]
            weight = req.session["weight"]
            contact = req.session["contactno"]
            address = req.session["address"]
            landmark = req.session["landmark"]
            district = req.session['district']
            state = req.session["state"]
            pincode = req.session["pincode"]


            newuser=User.objects.create_user(req.session["email"],req.session["email"],req.session["password"])
            newuser.first_name=req.session["name"]
            
            newuser.save()
            userlogin(req,req.session["email"],req.session["password"])
            # enter personal details here
            person = PersonalInfo()
            person.email= User.objects.get(username = email)
            person.name = name
            person.dob = dob
            person.weight = weight
            person.contact = contact
            person.address = address
            person.landmark = landmark
            person.district = district
            person.state = state
            person.pincode = pincode
            person.save()
            return redirect("/")

    
        else:
            return render(req,'otp.html',{"err":"Invalid OTP!!!"})
    
    return render(req,'otp.html')

def register(req):
    if req.method =="POST":
        email=req.POST['email']
        name=req.POST['name']
        contactno=req.POST['contactno']
        password=req.POST['password']
        dob=req.POST['dob']
        weight=req.POST['weight']
        address=req.POST['address']
        landmark=req.POST['landmark']
        district=req.POST['district']
        state=req.POST['state']
        pincode=req.POST['pincode']


        req.session["email"]=email
        req.session["name"]=name
        req.session["contactno"]=contactno
        req.session["password"]=password
        req.session["dob"]=dob
        req.session["weight"]=weight
        req.session["address"]=address
        req.session["landmark"]=landmark
        req.session["district"]=district
        req.session["state"]=state
        req.session["pincode"]=pincode



        try :
            user=User.objects.get(username=email)
            print(email,name,contactno,password)
            
            return render(req,"registration.html",{"err":"User already exist please login"})
        except :
            global otp 
            otp= random.randint(100000,999999)
            sendmail(otp,email)
            return render(req,'otp.html',{"msg": f"OTP sent to {email}" })



def conformOrder(req):
    if req.method == "POST":
        global otp
        otp=random.randint(100000,999999)
        req.session["address"]=req.POST['address']
        #req.session["doornum"]=req.POST['doornum',None]
        #req.session["street"]=req.POST['street']
        #req.session["town"]=req.POST['town']
        req.session["district"]=req.POST['district']
        req.session["state"]=req.POST['state']
        
        req.session["pincode"]=req.POST['pincode']
        
        #order = YourModel(doornum=doornum, street=street, town=town, district=district, state=state, pincode=pincode)
        #order.save()
        sub="Order Conformation For Online Pharmacy"
        body=f"<#> {otp} is your Online Pharmacy Order Verifivation code"
        print(f"{req.user}")
        emailhandler(f"{req.user}",sub,body)
        return redirect("/conformorderotp")
   
    
@login_required
def makepayment(req):
    user=req.user
    cart=Cart.objects.all().filter(user=user)
    count=cart.count()
    totalAmt=0
    for i in cart:
        totalAmt +=i.product.sellingprice * i.product_qty
    totalAmt *=100
    print(totalAmt)
    client = razorpay.Client(auth=("rzp_test_Pob9HvjFlghMtb", "KZWpRrJKHiGF2vi7oCnNcmVK"))
        
    DATA = {
        "amount": int(totalAmt) ,
        "currency": "INR",
        'payment_capture':'1',
        "receipt": "receipt#1",
        "notes": {
            "key1": "value3"
        }
    }
    payment=client.order.create(data=DATA)
    req.session["orderid"]=payment.get('id')
    # print(payment.get('id'))
    return render(req,"makepayment.html",{"totalAmt":totalAmt})


def conformOrderotp(req):
    print(otp,"-------------------------")
    if req.method == "POST":
        otp1=req.POST['otp']
        if otp == int(otp1): 
            return redirect("makepayment")    
        else:
            return render(req,'conformorderotp.html',{"err":"Invalid OTP!!!"})
    return render(req,'conformorderotp.html')


@login_required
@csrf_exempt
def addorder(req):
    if req.method == "POST":
        cart=Cart.objects.filter(user=req.user)
        count=cart.count()
        totalAmt=0
        for i in cart:
            totalAmt += i.product.sellingprice * i.product_qty
            print(i.pk)
        order= Orders()
        order.user=req.user
        order.orderid=req.session["orderid"]
        order.totalprice=totalAmt
        order.totalproducts=count
        order.address=req.session["address"]
        order.pincode=req.session["pincode"]
        order.save()
        print(Orders.objects.get(orderid=req.session["orderid"]))

        for i in cart:
            orderitems=Orderitems()
            orderitems.orderid=Orders.objects.get(orderid=req.session["orderid"])
            orderitems.product=Product.objects.get(id=i.product.pk)
            orderitems.quantity=i.product_qty
            orderitems.save()
            pro=Product.objects.get(id=i.product.pk)
            pro.stock -= i.product_qty
            pro.noofSales +=1
            print('----------------------------------------------------',pro.stock)
            pro.save()
            i.delete()
        return redirect("/thankyou")
    return redirect("makepayment")



def thankyouorder(req):
    return render(req,"thankyouorder.html")


def order(req):
    if req.user.is_authenticated :
        order=Orders.objects.filter(user=req.user).exclude(status=4).exclude(status=5)
        previous=Orders.objects.filter(user=req.user).exclude(status=1).exclude(status=2).exclude(status=3)
        print(previous)
        return render(req,"orders.html",{"order" : order,"previous" : previous,"ordercount" : order.count(),"pcount":previous.count()})    
    return render(req,"orders.html")

@login_required
def cancelorder(req):   
    if req.method == "POST" and Orders.objects.get(orderid=req.POST['cancelord']):
            req.session['cancelord']=req.POST['cancelord']
            print(req.session['cancelord'])
            return render(req,'cancelorder.html')
    else:
        return redirect('/orders')
  
    
@login_required
def updaterefund(req):
    if req.method == "POST" and Orders.objects.get(orderid=req.session['cancelord']):
            print(req.session['cancelord'])
            print(req.POST['upi'])
            print(req.POST['reason'])
            try :
                refund=Refund()
                refund.user=req.user
                refund.orderid=Orders.objects.get(orderid=req.session['cancelord'])
                refund.refundupi=req.POST['upi']
                refund.refundAmount=Orders.objects.get(orderid=req.session['cancelord']).totalprice
                refund.reason=req.POST['reason']
                refund.save()
                Orderitem=Orderitems.objects.filter(orderid=Orders.objects.get(orderid=req.session['cancelord']))
                for i in Orderitem:
                    product=Product.objects.get(id=i.product.pk)
                    product.stock += i.quantity
                    product.noofSales -= 1
                    product.save()                    
                    print("*************************************",i.product,i.quantity)
                order=Orders.objects.get(orderid=req.session['cancelord'])
                order.status=5
                order.save()
                subject="Refund From Online Pharmacy"
                msg=f"""Refund for OrderNo:{req.session['cancelord']} RS.{Orders.objects.get(orderid=req.session['cancelord']).totalprice} has been Successfully Refunded to Your UPI id {req.POST['upi']}"""
                print(msg)            
                emailhandler(f"{req.user}",subject,msg)
                return redirect('/orders')
            except:
                return redirect('/orders')
    else:
        return redirect('/orders')


def updatereviews(req,orderid,productid):
    order=Orders.objects.filter(user=req.user).get(orderid=orderid)
    orderItems=Orderitems.objects.filter(orderid=Orders.objects.get(orderid=orderid))    
    bool = True
    for i in orderItems:
        bool = bool & i.review    
    order.review=bool
    order.save()
    review=Review.objects.filter(product_name = productid)
    r=0
    for i in review:
        r += i.ratings
    print(r)
    r = r / review.count()
    print(r)
    if r <= 5 :
        product = Product.objects.get(id=productid)
        product.ratings = r
        product.save()


def invoice(req,orderid):
    if req.method == "POST":
        review=Review()
        review.name = req.user
        review.review = req.POST['review']
        review.ratings = int(req.POST['rating'] )
        review.product_name=Product.objects.get(id=req.POST['id'])
        review.save()        
        products=Orderitems.objects.filter(orderid=Orders.objects.get(orderid=orderid)).get(product=Product.objects.get(id=req.POST['id']))
        products.review=True
        products.save()
        updatereviews(req,orderid,req.POST['id'])
        print(products)
        redirect(f'invoice/{orderid}')
    order=Orders.objects.filter(orderid=orderid)
    print(order)
    if  order.count() == 0:
        return redirect('/orders')
    products=Orderitems.objects.filter(orderid=Orders.objects.get(orderid=orderid))
    return render(req,"invoice.html",{"order":order,"products":products})


@login_required
def logoutuser(req):
    logout(req)
    return redirect("/")


def randomguest():
    while True :
        id="gt-"+get_random_string(length=10)
        g=Guest.objects.filter(guestid=id)
        if len(g) > 0:
            continue
        return id


def guestsuccess(req):
    return render(req,"guestsuccess.html")


def guestreg(req):
    if req.method == "POST":
        guest = Guest()
        guest.guestname=req.POST['guestname']
        guest.guestid=randomguest()
        guest.guestPrescriptionImage=req.FILES.get("image") 
        guest.email=req.POST['email']
        guest.mobileno=req.POST['contactno']
        guest.address=req.POST['address']
        guest.pincode=req.POST['pincode']
        guest.save()
        return redirect('/guestsuccess')       
    return render(req,"guestreg.html")


def permitgt(req,gtid):
    try :
        order=Guest.objects.filter(guestid = gtid)
        products=GuestProducts.objects.filter(guestid = Guest.objects.get(guestid = gtid))
        return render (req,"guestagree.html",{"order" : order ,"products" : products})
    except:
        return render(req,"message.html",{"msg" :"Your order already Cancelled"})


def guestaction(req,action,gtid):
    try:
        order=Guest.objects.get(guestid = gtid)
        if order.agree :
            return render(req,"message.html",{"msg" :"Your order already Confirmed"})
        elif action == "agree":
            order.agree=True
            order.save()
        elif action == "disagree":
            order.delete()
            return render(req,"message.html",{"msg" :"Your Order has been succesfully cancelled"})
        return redirect('/guestsuccess')
    except :
        return render(req,"message.html",{"msg" :"Your order already Cancelled"})


def track(req):    
    if 'orderid' in req.GET:
            orderid=req.GET['orderid']
            order=Orders.objects.filter(orderid=orderid)
            if order.count() >0 :
                return render(req,"track.html",{"order":order})
            guest=Guest.objects.filter(guestid=orderid)
            if guest.count() >0 :
                return render(req,"track.html",{"guest":guest})
            
            return render(req,"track.html",{"err":"Please enter a valid or active Order Id"})    
    return render(req,"track.html")


def error_404 (req,exception):
    return render(req,"err404.html")


@login_required
def stats(req):
    stat=Summary.objects.get(id=1)
    print(stat)
    return render (req,"stats.html",{"stat":stat})