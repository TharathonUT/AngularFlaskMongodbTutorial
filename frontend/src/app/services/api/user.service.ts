import { Injectable } from '@angular/core';
import axiosClient from '../../httpclient/http-client';
import { Login } from 'src/app/interfaces/user';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  axios = axiosClient;

  constructor() { }

  async login(data:Login){
    let response = await this.axios.post(environment.API_IP+"/authen/login",data);
    if(response.status == 200){
      if (response.data.success) {
        localStorage.setItem("token",response.data.token);
        return true
      }
      return false
      
    }
    return false
  }

  async checkLogin(data:String){
    let response = await this.axios.post(environment.API_IP+"/authen/check",{"token":data});

    if (response.status == 200) {
      if (response.data.success) {
        return true
      }
      return false
    }
    return false
  }

  async getUserAll(){
    let test = await this.axios.get(environment.API_IP+"/users/");
    
    if(test.status == 200){
      const results:[] = test.data
      return results
    }
    return []
  }

  async UploadFile(form_data:FormData){
    let test = await this.axios.post(environment.API_IP+"/upload",form_data);
    if(test.status == 200){
      const results:[] = test.data
      return results
    }
    return []
  }
}
