package com.example.myapp.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.example.myapp.service.TtsService;

@RestController
@RequestMapping("/api")
public class ApiController {

    @Autowired
    private TtsService ttsService;

    @PostMapping("/speak")
    public ResponseEntity<String> speak(@RequestBody String text) {
        String response = ttsService.convertTextToSpeech(text);
        return ResponseEntity.ok(response);
    }
}