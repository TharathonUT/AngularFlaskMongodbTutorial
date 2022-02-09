import { Component, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { UserService } from '../../services/api/user.service';
import { ElementRef } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  
  constructor(private userApi: UserService) {
    
   }
  @ViewChild('videoPlayer') videoplayer!: ElementRef;
  uploadForm = new FormGroup({
    file: new FormControl('',[Validators.required]),
    file_source: new FormControl('',[Validators.required])
  });
  current_time = 0;
  total_time =0;
  video_interval:any;

  ngOnInit(): void {
    
  }

  onFileChange(event:any){
    console.log("select file");
    console.log(event);
    
    if(event.target.files.length >0){
      const file = event.target.files[0];
      this.uploadForm.patchValue({
        file_source: file
      })
    }
  }

  playVideo(){
    const media = this.videoplayer.nativeElement
    this.total_time = media.duration;
    console.log(media);
    //Fecth time from db
    // .. .. .. ..

    media.currentTime = 25; //Change 25 to time variable 
    if(media?.paused) {
      const self = this;
      this.video_interval = setInterval(function () {
        self.current_time = media.currentTime;
        //Send to db
      }, 5000);
      media?.play();
    } else {
      clearInterval(this.video_interval)
      media?.pause();
    }
  }

  onUpload(){
    console.log("Hello");
    const formData = new FormData();
    formData.append('file',this.uploadForm.get('file_source')?.value);
    formData.append('token','test');
    this.userApi.UploadFile(formData).then(()=>{
      alert("UPLOAD SUCCESS");
    })
  }
}
