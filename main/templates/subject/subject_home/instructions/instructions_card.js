
/**
 * Given the page number return the requested instruction text
 * @param pageNumber : int
 */
getInstructionPage(pageNumber){

    for(i=0;i<this.instruction_pages.length;i++)
    {
        if(this.instruction_pages[i].page_number==pageNumber)
        {
            return this.instruction_pages[i].text_html;
        }
    }

    return "Text not found";
},

/**
 * advance to next instruction page
 */
sendNextInstruction(direction){

    if(this.working) return;
    
    this.working = true;
    this.sendMessage("next_instruction", {"direction" : direction});
},

/**
 * advance to next instruction page
 */
takeNextInstruction(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;       
        
        this.session_player.current_instruction = result.current_instruction;
        this.session_player.current_instruction_complete = result.current_instruction_complete;

        this.processInstructionPage();
        this.instructionDisplayScroll();
    } 
    else
    {
        
    }
    
},

/**
 * finish instructions
 */
sendFinishInstructions(){

    if(this.working) return;
    
    this.working = true;
    this.sendMessage("finish_instructions", {});
},

/**
 * finish instructions
 */
takeFinishInstructions(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;       
        
        this.session_player.instructions_finished = result.instructions_finished;
        this.session_player.current_instruction_complete = result.current_instruction_complete;
    } 
    else
    {
        
    }
},

/**
 * process instruction page
 */
processInstructionPage(){

    //update view when instructions changes
    switch(this.session_player.current_instruction){
        case 1:            
            break; 
        case 2:
            break;
        case 3:            
            break;
        case 4:
            break; 
        case 5:           
            break;
        case 6:
            break;
    }

    if(this.session_player.current_instruction_complete < this.session_player.current_instruction)
    {
        this.session_player.current_instruction_complete = this.session_player.current_instruction;
    }

        
},

/**
 * scroll instruction into view
 */
instructionDisplayScroll(){
    
    if(document.getElementById("instructions_frame"))
        document.getElementById("instructions_frame").scrollIntoView();
    
    setTimeout(app.scroll_update, 500);
},

scroll_update()
{
    var scrollTop = document.getElementById('instructions_frame_a').scrollTop;
    var scrollHeight = document.getElementById('instructions_frame_a').scrollHeight; // added
    var offsetHeight = document.getElementById('instructions_frame_a').offsetHeight;
    // var clientHeight = document.getElementById('box').clientHeight;
    var contentHeight = scrollHeight - offsetHeight; // added
    if (contentHeight <= scrollTop) // modified
    {
        // Now this is called when scroll end!
        app.instruction_pages_show_scroll = false;
    }
    else
    {
        app.instruction_pages_show_scroll = true;
    }
},