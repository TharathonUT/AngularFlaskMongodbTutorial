import { Component, OnInit, Input } from '@angular/core';
import { User } from '../../interfaces/user';

@Component({
  selector: 'app-user-card',
  templateUrl: './user-card.component.html',
  styleUrls: ['./user-card.component.scss']
})
export class UserCardComponent implements OnInit {
  @Input() user_data:User = {};

  constructor() { }

  ngOnInit(): void {
  }

  
}
