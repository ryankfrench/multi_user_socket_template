send_chat(){

    if(app.working) return;
    if(app.chat_text.trim() == "") return;
    if(app.chat_text.trim().length > 200) return;
    
    app.working = true;
    app.send_message("chat", {"recipients" : app.chat_recipients,
                             "text" : app.chat_text.trim(),
                            });

    app.chat_text="";                   
},

/** take result of moving goods
*/
take_chat(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    if(message_data.value == "success")
    {
        app.take_update_chat(message_data);                        
    } 
    else
    {
        
    }
},

/** take updated data from goods being moved by another player
*    @param message_data {json} session day in json format
*/
take_update_chat(message_data){
    
    let chat = message_data.chat;
    app.session.world_state.session_players[chat.sender_id].show_chat = true;    
    app.session.world_state.session_players[chat.sender_id].chat_time = Date.now();
    app.session.world_state.session_players[chat.sender_id].pixi.chat_container.getChildAt(1).text = chat.text;
},

