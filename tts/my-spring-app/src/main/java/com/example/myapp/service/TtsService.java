package com.example.myapp.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class TtsService {

    private final String pythonServerUrl = "http://localhost:5000/tts"; // Adjust the URL as needed

    public String convertTextToSpeech(String text) {
        RestTemplate restTemplate = new RestTemplate();
        String response = restTemplate.postForObject(pythonServerUrl, text, String.class);
        return response;
    }
}