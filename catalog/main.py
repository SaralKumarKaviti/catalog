from flask import Flask,render_template,request, flash,redirect, url_for, jsonify
from flask_mysqldb import MySQL
import requests
import matplotlib.pyplot as plt
import io
import cv2
import numpy as np
# import mysql.connector
 
app = Flask(__name__)
 
app.config['MYSQL_HOST'] = 'scanner-iris-db.cj1kyfpqy43v.us-east-2.rds.amazonaws.com'
# app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Varsha123'
# app.config['MYSQL_PASSWORD'] = 'saral'
app.config['MYSQL_DB'] = 'retina_scanner'

# SQLALCHEMY_DATABASE_URI = 'mysql://root:@scanner-iris-db.cj1kyfpqy43v.us-east-2.rds.amazonaws.com/retina_scanner'
mysql = MySQL(app)

@app.route("/matchIris",methods=['POST','GET'])
def matchingIris():
    # conn =mysql.connect()
    # cursor=conn.cursor(pymysql.cursors.DictCursor)
    # msg=""
    # eyeImage=request.files['eyeImage']
    eyeImage="https://iris-scanner.s3.us-east-2.amazonaws.com/1/Right_Bitmap.bmp"
    # eyeImageUrl2=request.json['eyeImageUrl2']
    data_status={"responseStatus":0,"result":""}

    if request.method=="GET":
        cur = mysql.connection.cursor()
        cur.execute("""SELECT * FROM user WHERE left_eye = %s or right_eye = %s """, (eyeImage,eyeImage))
        # cur.execute("""SELECT * FROM user """)
        user = cur.fetchall()
        for i in user:
            print(i)

        # print(user)
        if user:
            data_status["responseStatus"]=1
            data_status["result"]="data fetched"
            data_status["ID"]=user[0]
            return data_status
        if not user:
            data_status["responseStatus"]=1
            data_status["result"]="No file"
            # data_status["data"]=user
            return data_status

            
    else:
        data_status["responseStatus"]=0
        data_status["result"]="mis matched"
        # return data_status
    return data_status

@app.route("/getImage",methods=['GET'])
def image():
    if request.method=="GET":
        cur = mysql.connection.cursor()
        # sql=
        # cursor = sql.cursor()
        cur.execute("""select image from retina_scanner.pictures where id={}""".format(2))
        # print(cursor)    
        myresult=cur.fetchone()[-1]
        storedfilepath=r"img1.bmp"
        print(myresult)
        with open(storedfilepath,"wb") as File:
            File.write(myresult)
            File.close()
        return File   


@app.route("/irisMaching",methods=['POST','GET'])
def irisMacthing():
    data_status={"responseStatus":0,"result":""}
    eyeImage=request.files["eyeImage"]
    npimg = np.fromfile(eyeImage, np.uint8)
    file3 = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    # print(eyeImage)
    if request.method=="POST":
        query ="select id,left_eye,right_eye from retina_scanner.user"
        cursor=mysql.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        # id_query="select id from retina_scanner.user"
        # cursor.execute(id_query)
        # ids = cursor.fetchall()
        # print(data)
        ids_list=[]
        for i in data:
            data_list=[]
            for n in i.items():
                data_list.append(n[1])
            for d in data_list[1:]:    

                #print(str(j))
                def orb_sim(img1, img2):
                    # SIFT is no longer available in cv2 so using ORB
                    orb = cv2.ORB_create()

                    # 714 x 901 pixels

                    # detect keypoints and descriptors
                    kp_a, desc_a = orb.detectAndCompute(img1, None)
                    kp_b, desc_b = orb.detectAndCompute(img2, None)

                    # define the bruteforce matcher object
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

                    # perform matches.
                    matches = bf.match(desc_a, desc_b)
                    # Look for similar regions with distance < 50. Goes from 0 to 100 so pick a number between.
                    similar_regions = [i for i in matches if i.distance < 50]
                    if len(matches) == 0:
                        return 0
                    return len(similar_regions) / len(matches)
                print(n)    
                response = requests.get(d).content
                img = plt.imread(io.BytesIO(response), format='bmp')
                # obj=cv2.imread(eyeImage)
                # npimg = np.fromfile(eyeImage, np.uint8)
                # file3 = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                orb_similarity = orb_sim(img,file3)
                #print(orb_similarity)
                if orb_similarity > 0.80:
                    
                    data_status["responseStatus"]=1
                    data_status["result"]="Matched"
                    data_status["ordSimilarity"]=orb_similarity
                    data_status["imageName"]=d[:-4].split("/")[-1]
                    data_status["id"]=data_list[1]
                    if d==data_list[1]:

                        data_status["matchFrom"]="Image from Left eye"
                    else:
                        data_status["matchFrom"]="Image from Right eye"    
                    return data_status

                else:
                    continue
                    # data_status["responseStatus"]=0
                    # data_status["ordSimilarity"]=orb_similarity
                    # data_status["result"]="Not matched"
                    # return data_status




    else:
        data_status["responseStatus"]=0
    data_status["result"]="File Match not found"
    return data_status

@app.route("/irisMaching_old",methods=['POST','GET'])
def irisMacthingOld():
    data_status={"responseStatus":0,"result":""}
    eyeImage=request.files["eyeImage"]
    npimg = np.fromfile(eyeImage, np.uint8)
    file3 = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    # print(eyeImage)
    if request.method=="POST":
        query ="select id,left_eye,right_eye from retina_scanner.user"
        cursor=mysql.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        # id_query="select id from retina_scanner.user"
        # cursor.execute(id_query)
        # ids = cursor.fetchall()
        print(data)
        ids_list=[]
        for i in data:
            for n in (i[1:]):
                #print(str(j))
                def orb_sim(img1, img2):
                    # SIFT is no longer available in cv2 so using ORB
                    orb = cv2.ORB_create()

                    # 714 x 901 pixels

                    # detect keypoints and descriptors
                    kp_a, desc_a = orb.detectAndCompute(img1, None)
                    kp_b, desc_b = orb.detectAndCompute(img2, None)

                    # define the bruteforce matcher object
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

                    # perform matches.
                    matches = bf.match(desc_a, desc_b)
                    # Look for similar regions with distance < 50. Goes from 0 to 100 so pick a number between.
                    similar_regions = [i for i in matches if i.distance < 50]
                    if len(matches) == 0:
                        return 0
                    return len(similar_regions) / len(matches)
                print(n)    
                response = requests.get(n).content
                img = plt.imread(io.BytesIO(response), format='bmp')
                # obj=cv2.imread(eyeImage)
                # npimg = np.fromfile(eyeImage, np.uint8)
                # file3 = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                orb_similarity = orb_sim(img,file3)
                #print(orb_similarity)
                if orb_similarity > 0.80:
                    
                    data_status["responseStatus"]=1
                    data_status["result"]="Matched"
                    data_status["ordSimilarity"]=orb_similarity
                    data_status["imageName"]=n[:-4].split("/")[-1]
                    data_status["id"]=i[0]
                    if n==i[1]:

                        data_status["matchFrom"]="Image from Left eye"
                    else:
                        data_status["matchFrom"]="Image from Right eye"    
                    return data_status

                else:
                    continue
                    # data_status["responseStatus"]=0
                    # data_status["ordSimilarity"]=orb_similarity
                    # data_status["result"]="Not matched"
                    # return data_status




    else:
        data_status["responseStatus"]=0
    data_status["result"]="File Match not found"
    return data_status        




if __name__=='__main__':
    app.run(debug=True)
    