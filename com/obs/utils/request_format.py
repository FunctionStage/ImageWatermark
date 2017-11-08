#!/usr/bin/python
# -*- coding:utf-8 -*-

from com.obs.models.base_model import IS_PYTHON2

if IS_PYTHON2:
    import urllib
else:
    import urllib.parse as urllib

#===============================================================================
# 请求格式，发送HTTP请求时，URL是路径模式或者子域名格式
#===============================================================================
class RequestFormat(object):
    
    @staticmethod       
    def get_pathformat():
        return PathFormat()
    
    @staticmethod
    def get_subdomainformat():
        return SubdomainFormat()
    
    @staticmethod
    def get_vanityformat():
        return VanityFormat()

    # ===========================================================================
    # 将路径参数从map类型转换为字符串
    # @path_args 参数hash表
    # @return    转换后的路径参数字符串
    # ===========================================================================
    @classmethod
    def convert_path_string(cls, path_args, allowdNames=None, safe=' ,:?/=+&%'):
        e = ''
        if isinstance(path_args, dict):
            e1 = '?'
            e2 = '&'
            for path_key, path_value in path_args.items():
                flag = True
                if allowdNames is not None and path_key not in allowdNames:
                    flag = False
                if flag:
                    path_key = urllib.quote(str(path_key), safe)
                    if path_value is None:
                        e1 += path_key + '&'
                        continue
                    e2 += path_key + '=' + urllib.quote(str(path_value), safe) + '&'
            e = (e1 + e2).replace('&&', '&').replace('?&', '?')[:-1]
        return e

    @classmethod
    def toString(cls,item):
        try:
            return str(item) if item is not None else ''
        except:
            return ''

    @classmethod
    def encode_object_key(cls, key):
        return urllib.quote(cls.toString(key), ',:?/=+&%')

    def supports_locatedbuckets(self):
        '''
        '''
        return

    def get_endpoint(self, server, port, bucket):
        '''
        '''
        return
    
    def get_pathbase(self, bucket, key):
        '''
        '''
        return
    
    def get_url(self, bucket, key, path_args):
        '''
        '''
        return
    
#==========================================================================
# 请求方式类，路径请求方式。
# 带对象和存储空间的请求为：s3.xxxx.com/bucketname/key
# 不带对象，带存储空间的请求为：s3.xxxx.com/bucketname/
# 不带存储空间和对象的的请求为：s3.xxxx.com/
#==========================================================================  
class PathFormat(RequestFormat):
       
    def supports_locatedbuckets(self):
        return True 
    
    def get_server(self, server, bucket):
        return server
       
    def get_pathbase(self, bucket, key):
        if not bucket:
            return '/'
        if key is None:
            return '/' + bucket
        return '/' + bucket + '/' + self.encode_object_key(key)

    def get_endpoint(self, server, port, bucket):
        return server + ':' + str(port)

    #===========================================================================
    # 获得相对url
    #===========================================================================
    def get_url(self, bucket, key, path_args):
        path_base = self.get_pathbase(bucket, key)
        path_arguments = self.convert_path_string(path_args)
        return path_base + path_arguments
    
    #===========================================================================
    # 获得绝对url  完整路径
    #===========================================================================
    def get_full_url(self, is_secure, server, port, bucket, key, path_args):    
        url = 'https://' if is_secure else 'http://'
        url += self.get_endpoint(server, port, bucket)
        url += self.get_url(bucket, key, path_args)
        return url

#===============================================================================
# 请求方式类，子域请求方式。
# 带对象和存储空间的请求为：bucketname.s3.xxxx.com/key
# 不带对象，带存储空间的请求为：bucketname.s3.xxxx.com/
# 不带存储空间和对象的的请求为：s3.xxxx.com/
#===============================================================================
class SubdomainFormat(RequestFormat):
       
    def supports_locatedbuckets(self):
        return True 

    def get_server(self, server, bucket):
        return bucket + '.' + server if bucket else server

    def get_pathbase(self, bucket, key):
        if key is None:
            return '/'
        return '/' + self.encode_object_key(key)

    def get_endpoint(self, server, port, bucket):
        return self.get_server(server, bucket) + ':' + str(port)
    
    #===========================================================================
    # 获得相对url
    #===========================================================================
    def get_url(self, bucket, key, path_args):
        url = self.convert_path_string(path_args)
        return self.get_pathbase(bucket, key) + url if bucket else url

    #===========================================================================
    # 获得绝对url 完整路径
    #===========================================================================
    def get_full_url(self, is_secure, server, port, bucket, key, path_args):
        url = 'https://' if is_secure else 'http://'
        url += self.get_endpoint(server, port, bucket)
        url += self.get_url(bucket, key, path_args)
        return url

   
           
class VanityFormat(SubdomainFormat):
           
    def get_server(self, server, bucket):
        return bucket

