from marshmallow import Schema,fields
from application.apps.users.models import User,UserProfile

# 基于Schema完成数据序列化转换
# class UserSchema(Schema):
#     name = fields.String()
#     age = fields.Integer()
#     email = fields.Email()
#     money = fields.Number()
#
#     class Meta:
#         fields = ["name", "age", "money", "email", "info"]
#         ordered = True  # 转换成有序字典
#
#
# def index():
#     """序列化"""
#     """单个模型数据的序列化处理"""
#     user1 = User(name="xiaoming", password="123456", age=16, email="333@qq.com", money=31.50)
#     # print(user1)
#     # 把模型对象转换成字典格式
#     data1 = UserSchema().dump(user1)
#     print(type(data1), data1)
#
#     # 把模型对象转换成json字符串格式
#     data2 = UserSchema().dumps(user1)
#     print(type(data2), data2)
#     return data2


# *************** 多个模型数据的序列化 ******************************
# class UserSchema(Schema):
#     name   = fields.String()
#     age    = fields.Integer()
#     email  = fields.Email()
#     money  = fields.Number()
#     class Meta:
#         fields = ["name","age","money","email","info"]
#         ordered = True # 转换成有序字典
# def index():
#     """序列化"""
#     """多个模型数据的序列化"""
#     user1 = User(name="xiaoming", password="123456", age=15, email="333@qq.com", money=31.50)
#     user2 = User(name="xiaohong", password="123456", age=16, email="333@qq.com", money=31.50)
#     user3 = User(name="xiaopang", password="123456", age=17, email="333@qq.com", money=31.50)
#     data_list = [user1,user2,user3]
#     data1 = UserSchema(many=True).dumps(data_list)
#     print(type(data1),data1)
#     return "ok"

# ******************** 构造器嵌套使用 ******************

# class UserProfileSchema(Schema):
#     education = fields.Integer()
#     middle_school = fields.String()
#
# class UserSchema(Schema):
#     name   = fields.String()
#     age    = fields.Integer()
#     email  = fields.Email()
#     money  = fields.Number()
#     info   = fields.Nested(UserProfileSchema,only=["middle_school"])
#     class Meta:
#         fields = ["name","age","money","email","info"]
#         ordered = True # 转换成有序字典
#
# def index():
#     """序列化"""
#     """序列化嵌套使用"""
#     user1 = User(name="xiaoming", password="123456", age=15, email="333@qq.com", money=31.50)
#     user1.info = UserProfile(
#         education=3,
#         middle_school="北京师范学院附属中学白沙路分校"
#     )
#     data = UserSchema().dump(user1)
#     data = UserSchema().dumps(user1)
#     print(data)
#     return "ok"

# ************** 给予Schema 完成数据反序列化转换 ********************

# from marshmallow import Schema, fields, validate, ValidationError, post_load
#
#
# class UserSchema2(Schema):
#     name = fields.String()
#     sex = fields.String()
#     age = fields.Integer(missing=18)
#     email = fields.Email()
#     mobile = fields.String()
#
#     # 有点像序列化使用的钩子,在指定的时机执行
#     @post_load
#     def post_load(self, data, **kwargs):
#         return User(**data)
#
# ************** partial **************
# def index():
#     user_data = {"mobile": "1331345635", "name": "xiaoming", "email": "xiaoming@qq.com", "sex": "abc"}
#     us2 = UserSchema2()
#     result = us2.load(user_data)
#     print(result)  # ==> <User xiaoming>通过钩子使得反序列化后得到的是对象
#     return "ok"

# from marshmallow import Schema, fields, validate, ValidationError,post_load
# class UserSchema2(Schema):
#     name = fields.String()
#     sex = fields.String()
#     age = fields.Integer(missing=18)
#     email = fields.Email()
#     mobile = fields.String(required=True)
#
#     # @post_load
#     # def post_load(self, data, **kwargs):
#     #     return User(**data)
#
# def index():
#     user_data = {"name": "xiaoming","sex":"abc"}
#     us2 = UserSchema2()
#     # partial: 只校验user_data 有的数据
#     # 因为正常反序列化,通过序列化器反序列化时,数据要全部都在序列化器字段存在
#     result = us2.load(user_data,partial=True)
#     print(result)  # ==> <User xiaoming>
#     return "ok"

# ************** 设置字段只在序列化或反序列化阶段才启用 **********************
# from marshmallow import Schema, fields, validate, ValidationError,post_load
# class UserSchema2(Schema):
#     name = fields.String()
#     sex = fields.Integer(validate=validate.OneOf([0,1,2]))
#     age = fields.Integer(missing=18)
#     email = fields.Email()
#     mobile = fields.String()
#     password = fields.String(load_only=True) # 设置当前字段为只写字段，只会在反序列化阶段启用
#
#     @post_load
#     def post_load(self, data, **kwargs):
#         return User(**data)
#
# def index():
#     user_data = {"name": "xiaoming","password":"123456","sex":1}
#     us2 = UserSchema2()
#     # 反序列化
#     result = us2.load(user_data)
#     print(result)  # ==> <User xiaoming>
#     # 序列化
#     us3 = UserSchema2(only=["sex","name","age"]) # 限制处理的字段
#     result2 = us3.dump(result)
#     print(result2)
#     return "ok"
#
#     # # password = fields.Str(load_only=True) # 相当于只写字段 "write-only"
#     # # created_time = fields.DateTime(dump_only=True) # 相当于只读字段 "read-only"

# *********** 反序列化阶段的钩子方法 ********************

# post_dump([fn，pass_many，pass_original]) 注册要在序列化对象后调用的方法，它会在对象序列化后被调用。
# post_load([fn，pass_many，pass_original]) 注册反序列化对象后要调用的方法，它会在验证数据之后被调用。
# pre_dump([fn，pass_many]) 注册要在序列化对象之前调用的方法，它会在序列化对象之前被调用。
# pre_load([fn，pass_many]) 在反序列化对象之前，注册要调用的方法，它会在验证数据之前调用。

# from marshmallow import Schema, fields, validate, ValidationError,post_load,post_dump
# class UserSchema2(Schema):
#     name = fields.String()
#     sex = fields.Integer(validate=validate.OneOf([0,1,2]))
#     age = fields.Integer(missing=18)
#     email = fields.Email()
#     mobile = fields.String()
#     password = fields.String(load_only=True) # 设置当前字段为只写字段，只会在反序列化阶段启用
#
#     @post_load
#     def post_load(self, data, **kwargs):
#         return User(**data)
#
#     @post_dump
#     def post_dump(self, data, **kwargs):
#         # 序列化器序列化后,再把手机号弄成 135*****333
#         data["mobile"] = data["mobile"][:3]+"*****"+data["mobile"][-3:]
#         return data
# def index():
#     user_data = {"name": "xiaoming","password":"123456","sex":1,"mobile":"133123454656"}
#     us2 = UserSchema2()
#     # 反序列化
#     result = us2.load(user_data)
#     print(result)
#     # 序列化
#     us3 = UserSchema2(only=["sex","name","age","mobile"])
#     result2 = us3.dump(result)
#     print(result2)
#     return "ok"

# --------------- 反序列化阶段对数据进行验证 -----------------
# *************** 基于内置验证器进行数据验证 *****************

# from marshmallow import Schema, fields, validate, ValidationError,post_load
# class UserSchema3(Schema):
#     name = fields.String(required=True)
#     sex = fields.String(required=True,error_messages={"required":"对不起，permission必须填写"})
#     age = fields.Integer(missing=18,validate=validate.Range(min=18,max=40,error="年龄必须在18-40之间！")) # 限制数值范围
#     email = fields.Email(error_messages={"invalid":"对不起，必须填写邮箱格式！"})
#     mobile = fields.String(required=True, validate=validate.Regexp("^1[3-9]\d{9}$",error="手机号码格式不正确"),error_messages={"Regexp":"手机格式不正确"})
#
#     @post_load
#     def make_user_obj(self, data, **kwargs):
#         return User(**data)
#
# def index3():
#     user_data = {"mobile":"1331345635","name": "xiaoming","age":40, "email": "xiaoming@qq.com","sex":"abc"}
#     us2 = UserSchema3()
#     result = us2.load(user_data)
#     result2 = us2.dumps(result)
#     print(result)
#     print(result2)
#     return "ok"

# ************************* 自定义验证方法 *************************

# from marshmallow import Schema, fields, validate,validates, ValidationError,post_load,validates_schema
# class UserSchema4(Schema):
#     name = fields.String(required=True)
#     sex = fields.String(required=True,error_messages={"required":"对不起，permission必须填写"})
#     age = fields.Integer(missing=18,validate=validate.Range(min=18,max=40,error="年龄必须在18-40之间！")) # 限制数值范围
#     email = fields.Email(error_messages={"invalid":"对不起，必须填写邮箱格式！"})
#     mobile = fields.String(required=True, validate=validate.Regexp("^1[3-9]\d{9}$",error="手机号码格式不正确"),error_messages={"Regexp":"手机格式不正确"})
#     password = fields.String(required=True, load_only=True)
#     password2 = fields.String(required=True, allow_none=True)
#     @post_load
#     def make_user_obj(self, data, **kwargs):
#         return User(**data)
#
#     @validates("name")
#     def validate_name(self,data,**kwargs):
#         print("name=%s" % data)
#         if data == "root":
#             raise ValidationError({"对不起,root用户是超级用户!您没有权限注册！"})
#
#         # 必须有返回值
#         return data
#
#     @validates_schema
#     def validate(self,data,**kwargs):
#         print('********8')
#         print(data)
#         if data["password"] != data["password2"]:
#             raise ValidationError("密码和确认密码必须一样！")
#
#         data.pop("password2")
#         return data
#
# def index():
#     user_data = {"password":"123456","password2":"123456","mobile":"13313345635","name": "root1","age":40, "email": "xiaoming@qq.com","sex":"abc"}
#     us2 = UserSchema4()
#     result = us2.load(user_data)
#     print(result)
#     return "ok"

# from marshmallow_sqlalchemy import SQLAlchemySchema,SQLAlchemyAutoSchema,auto_field
# class UserSchema5(SQLAlchemySchema):
#     username = auto_field("name",dump_only=True)
#     created_time = auto_field(format="%Y-%m-%d")
#     token = fields.String()
#     class Meta:
#         model = User
#         fields = ["username","created_time","token"]
# def index():
#     """ 单个模型数据的序列化处理 """
#     from datetime import datetime
#     user1 = User(
#         name="xiaoming",
#         password="123456",
#         age=16,
#         email="333@qq.com",
#         money=31.50,
#         created_time=datetime.now(),
#     )
#     user1.token = "abc"
#     # 把模型对象转换成字典格式
#     data1 = UserSchema5().dump(user1)
#     print(type(data1),data1)
#     return "ok"

from marshmallow_sqlalchemy import SQLAlchemySchema,SQLAlchemyAutoSchema,auto_field
from application import db
class UserSchema6(SQLAlchemyAutoSchema):
    token = fields.String()
    class Meta:
        model = User
        include_fk = False # 启用外建关系
        include_relationships = False # 模型关系外部属性
        fields = ["name","created_time","info","token"] # 如果要换成全部字段,就不要生命fields或exclude字段即可
        sql_session = db.session

def index():
    from datetime import datetime
    user1 = User(
        name="xiaoming",
        password="123456",
        age=16,
        email="333@qq.com",
        money=31.50,
        created_time=datetime.now(),
        info=UserProfile(position="助教")
    )
    # 把模型对象转换成字典格式
    user1.token = "abbbbb"
    data1 = UserSchema6().dump(user1)
    # <class 'dict'> {'created_time': '2020-12-02T17:35:02.709137',
    # 'info': <UserProfile: None>, 'name': 'xiaoming', 'token': 'abbbbb'}
    print(type(data1), data1)
    return "ok"

