#include "stm32f4xx.h"

int data;
int i;

volatile uint32_t ms_ticks = 0; // A millisecond counter
uint32_t last_peak_time = 0;     // Time when the last peak was detected
uint8_t peak_detected = 0;       // A flag to prevent multiple detections of the same peak
int heart_rate = 0;              // The calculated BPM
int peak_threashold = 200;

void SysTick_Handler(void) {
    ms_ticks++; // Increment our millisecond counter
}

int main(void) {
    RCC->AHB1ENR |= (7U << 0);
    RCC->APB2ENR |= (1 << 8);
		RCC->APB1ENR |= (1<<17);
		SysTick_Config(16000);
    
    GPIOA->MODER |= (3U << 0);
		GPIOB->MODER |= (1<<18);
		GPIOC->MODER |= (5<<26);
		GPIOA->MODER |= (1<<5);
	
		GPIOA->AFR[0] |= (7<<8);
		USART2->BRR = 0x0683;
		USART2->CR1 |= (1<<3);
		USART2->CR1 |= (1<<13);
		
    ADC1->SMPR2 = 0;
		ADC->CCR = 0;
    ADC1->CR1 = 0;
    ADC1->CR2 = 0;
    ADC1->CR2 |= (1U << 1); 
    ADC1->SQR3 = 0; 
    ADC1->SQR1 = 0;
    ADC1->CR2 |= 1;
		ADC1->CR1 |= (2<<24);
    while((ADC1->CR2 & 1) == 0) {}
    ADC1->CR2 |= (1 << 30);
			
    while (1) {
        while (!(ADC1->SR & (1 << 1)));
				data = ADC1->DR;
				if (data<150 && data>100) data=125;
			
				if (data > peak_threashold && peak_detected == 0) {
        // A peak is detected!
        uint32_t current_peak_time = ms_ticks;
        
        // Make sure enough time has passed to avoid noise (e.g., > 300ms, which is 200 BPM)
        if ((current_peak_time - last_peak_time) > 300) {

            // Calculate the time difference in milliseconds
            uint32_t rr_interval_ms = current_peak_time - last_peak_time;
            
            // Calculate BPM
            // (60 seconds/minute * 1000 ms/second) / interval in ms
            heart_rate = 60000 / rr_interval_ms;
            
            // Update the time of the last peak
            last_peak_time = current_peak_time;

            // Transmit the new heart rate value
						
					while (!(USART2->SR & (1<<7)));
					USART2->DR = 130;
            while (!(USART2->SR & (1<<7)));
            USART2->DR = heart_rate; // Send the BPM value
        }
        
        peak_detected = 1; // Set the flag to avoid re-detecting this same peak
    } 
    // If the signal drops below the threshold, we can look for a new peak
    else if (data < peak_threashold) {
        peak_detected = 0; // Reset the flag
    }
					
				while (!(USART2->SR & (1<<7)));
				USART2->DR = data;
				
				for (i=0; i<200000; i++);
    }
}