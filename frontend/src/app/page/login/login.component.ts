import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { UserService } from 'src/app/services/api/user.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  loginForm = new FormGroup({
    username: new FormControl('', [Validators.required]),
    password: new FormControl('', [Validators.required]),
  });
  users = [];

  constructor(private userApi: UserService) {}

  ngOnInit(): void {}

  async onLogin() {
    !this.loginForm.valid ? alert('Fill form!') : null;
    console.log(this.loginForm.value, this.loginForm.valid);
    let isSuccess = await this.userApi.login(this.loginForm.value);
    if (!isSuccess) {
      return alert("Login failed");
    }
  }
  async getAllUser() {
    this.users = await this.userApi.getUserAll();
  }
}
