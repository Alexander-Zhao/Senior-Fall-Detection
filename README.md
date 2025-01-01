# Senior-Fall-Detection


 Using MIT App Inventor, I developed a mobile app that contacts emergency services when a fall is detected. The system integrates an accelerometer sensor with a Raspberry Pi Pico W, running a Python-based fall detection algorithm. Upon detecting a fall, the Pico W sends data to the smartphone app, which then triggers alerts via email and phone calls to emergency contacts.
Initially, I implemented a threshold-based detection method, identifying falls based on fixed values of 3-axis acceleration data. While effective as a starting point, this method lacked adaptability to various fall scenarios, such as different types of falls or individual physical characteristics. To address these limitations, I expanded the system to include 6-axis data by integrating 3-axis gyroscope measurements alongside 3-axis acceleration data.
I collected and labeled 200 fall and non-fall events to build a robust dataset for training and testing Machine Learning models. I then applied five ML algorithms: Random Forests, Decision Tree, Support Vector Machines (SVM), Logistic Regression, and K-Nearest Neighbors. The ML-based detection system achieved a 40% improvement in accuracy over the threshold-based method. Among these models, Random Forest demonstrated the highest performance, achieving 97% accuracy across a variety of scenarios.




![image](https://github.com/user-attachments/assets/9f89503e-c66e-4229-8697-37ca4c2abfaa)



![image](https://github.com/user-attachments/assets/ba68ff9f-b323-463a-b226-e5e112677607)



![image](https://github.com/user-attachments/assets/cac41be9-60d5-4528-88a7-f2684b401748)



![image](https://github.com/user-attachments/assets/9f8b1bba-3877-4381-8225-86ce5669666c)



![image](https://github.com/user-attachments/assets/91dc8676-5d7f-483e-980d-70fead1c4625)
