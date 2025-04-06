#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE image_copy[height][width];
    int gx_array[] = {-1, 0, 1, -2, -1, 0, 1};
    int gy_array[] = {-1, -2, -1, 0, 0, 0, 1, 2, 1};
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int gx_red = 0, gx_green = 0, gx_blue = 0, gy_red = 0, gy_green = 0, gy_blue = 0;
            int counter = 0;
            for (int updated_i = i - 1; updated_i < i + 2; updated_i++)
            {
                for (int updated_j = j - 1; updated_j < j + 2; updated_j++)
                {
                    if (!(updated_i < 0 || updated_j < 0 || updated_i >= height ||
                          updated_j >= width))
                    {
                        gx_red += gx_array[counter] * image[updated_i][updated_j].rgbtRed;
                        gx_green += gx_array[counter] * image[updated_i][updated_j].rgbtGreen;
                        gx_blue += gx_array[counter] * image[updated_i][updated_j].rgbtBlue;
                        gx_red += gx_array[counter] * image[updated_i][updated_j].rgbtRed;
                        gx_green += gx_array[counter] * image[updated_i][updated_j].rgbtGreen;
                        gx_blue += gx_array[counter] * image[updated_i][updated_j].rgbtBlue;
                    }
                    counter++;
                }
            }
            int final_red = round(sqrt(pow(gx_red, 2) + pow(gy_red, 2)));
            int final_green = round(sqrt(pow(gx_green, 2) + pow(gy_green, 2)));
            int final_blue = round(sqrt(pow(gx_blue, 2) + pow(gy_blue, 2)));

            image_copy[i][j].rgbtRed = (final_red > 255) ? 255 : final_red;
            image_copy[i][j].rgbtGreen = (final_green > 255) ? 255 : final_green;
            image_copy[i][j].rgbtBlue = (final_blue > 255) ? 255 : final_blue;
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < height; j++)
        {
            image[i][j] = image_copy[i][j];
        }
    }
    return;
}
