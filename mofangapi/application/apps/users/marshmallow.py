from marshmallow import Schema,fields,validate,validates,ValidationError
from message import ErrorMessage as Message
from .models import User,db
class MobileSchema(Schema):
    mobile = fields.String(required=True,validate=validate.Regexp("^1[3-9]\d{9}$",error=Message.mobile_format_error))

    @validates("mobile")
    def validates_mobile(self,data):
        user = User.query.filter(User.mobile==data).first()
        print("*********")
        print(user)
        print("********")
        if user is not None:
            raise ValidationError(message=Message.mobile_is_use)
        return data

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema,auto_field
from marshmallow import post_load,pre_load,validates_schema

# 保存用户注册信息接口
class UserSchema(SQLAlchemyAutoSchema):
    mobile = auto_field(required=True, load_only=True)
    password = fields.String(required=True, load_only=True)
    password2 = fields.String(required=True, load_only=True)
    sms_code = fields.String(required=True, load_only=True)

    class Meta:
        model = User
        include_fk = True # 启用外键关系
        include_relationships = True  # 模型关系外部属性
        fields = ["id", "name", "mobile", "password", "password2", "sms_code"]  # 如果要全换全部字段，就不要声明fields或exclude字段即可
        sql_session = db.session
    # 反序列化校验结束后,要把反序列化的确认密码和验证码移除,把用户名初始化,保存到数据库
    @post_load()
    def save_object(self,data,**kwargs):
        data.pop("password2")
        data.pop("sms_code")
        data["name"] = data["mobile"]
        instance = User(**data)
        db.session.add(instance)
        db.session.commit()
        return instance

    # 校验
    @validates_schema
    def validate(self,data,**kwargs):
        # 校验密码和确认密码
        if data["password"] != data["password2"]:
            raise ValidationError(message=Message.password_not_match,fields_name="password")

        # todo 校验短信验证码

        return data


