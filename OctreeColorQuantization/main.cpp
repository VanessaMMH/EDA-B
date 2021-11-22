#include "QuantizationOctree.hpp"

#include <opencv2/highgui.hpp>
#include <iostream>

int main(int argc, char *argv[])
{
    cv::Mat image;
    std::string file_name = argv[1];
    image = cv::imread(file_name, CV_LOAD_IMAGE_COLOR);

    if (!image.data)
    {
        std::cout << "Could not open or find the image" << std::endl;
        return -1;
    }

    QuantizationOctree quantization;

    quantization.fill(image);

    quantization.reduction();
    quantization.reduction();
    quantization.reduction();
    quantization.reduction();
    quantization.reduction();
    quantization.reduction();

    cv::Mat palette(0, 500, CV_8UC3, cv::Scalar(0,0,0));

    quantization.get_palette(palette);
    cv::namedWindow("Paleta", cv::WINDOW_AUTOSIZE);
    cv::imshow("Paleta", palette);

    quantization.reconstruction(image);

    cv::namedWindow("Color Quantization", cv::WINDOW_AUTOSIZE);
    cv::imshow("Color Quantization", image);

    cv::Mat original;
    original = cv::imread(file_name, CV_LOAD_IMAGE_COLOR);

    cv::namedWindow("Original", cv::WINDOW_AUTOSIZE);
    cv::imshow("Original", original);

    cv::waitKey(0);

    return 0;
}