import React, { useEffect, useRef } from "react";
import Message from "./Message";

const MessageList = ({ messages }) => {

    const messagesEndRef = useRef(null);

    const scrolltoBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };
    
    useEffect(() => {
        scrolltoBottom();
    }, [messages]);

    return(
        <div style = {{
            flex: 1,
            overflowY: 'auto',
            padding: '15px',
            display: 'flex',
            backgroundColor: '#E0EAFC',
            flexDirection: 'column',
            gap: '10px',
        }}>
        
        { messages.map((msg) => (
            <Message 
            key = {msg.id} 
            message = {msg} 
            style = {{
                display: 'flex',
                justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
            }}
            
            />
        ))}

            <div ref={messagesEndRef} />

        </div>
    );
};

export default MessageList;
