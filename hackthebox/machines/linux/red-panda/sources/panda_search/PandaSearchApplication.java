package com.panda_search.htb.panda_search;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;
import org.springframework.web.servlet.handler.HandlerInterceptorAdapter;

@SpringBootApplication
public class PandaSearchApplication extends WebMvcConfigurerAdapter{
	@Override
	public void addInterceptors (InterceptorRegistry registry) {
		registry.addInterceptor(new RequestInterceptor());
	}

	public static void main(String[] args) {
		SpringApplication.run(PandaSearchApplication.class, args);
	}

}
