#include <opencv2/highgui.hpp>

uchar getIndex(uchar r, uchar g, uchar b, uchar level)
{
    // 128 == 10000000 in binary
    uchar index = 0;
    uchar mask = (uchar)128 >> level;
    if (r & mask)
        index |= (uchar)4;
    if (g & mask)
        index |= (uchar)2;
    if (b & mask)
        index |= (uchar)1;

    return index;
}

struct Color
{
    uint r;
    uint g;
    uint b;

    Color()
    {
        r = g = b = 0;
    }

    Color(uchar r, uchar g, uchar b)
    {
        this->r = r;
        this->g = g;
        this->b = b;
    }
};

struct ColorNode
{
    int level;
    int pixelCount;
    Color color;
    bool isLeaf;
    ColorNode *childs[8];

    ColorNode()
    {
        level = 0;
        pixelCount = 0;
        color = Color(0, 0, 0);
        isLeaf = false;
        for (int i = 0; i < 8; i++)
            childs[i] = nullptr;
    }
    void search_color(cv::Mat &palette);

    ~ColorNode();

    ColorNode(int level, int pixelCount, Color color, bool isLeaf)
    {
        this->level = level;
        this->pixelCount = pixelCount;
        this->color = color;
        this->isLeaf = isLeaf;

        for (int i = 0; i < 8; i++)
            childs[i] = nullptr;
    }

    void add_level(int height);
    void delete_level();
};

ColorNode::~ColorNode()
{
    if (isLeaf)
        return;

    for (int i = 0; i < 8; i++)
        delete childs[i];
}

void ColorNode::search_color(cv::Mat &palette)
{
    if (isLeaf)
    {
        if (pixelCount > 0)
        {
            uchar colorb = (color.b) / (pixelCount);
            uchar colorg = (color.g) / (pixelCount);
            uchar colorr = (color.r) / (pixelCount);
            palette.push_back(cv::Mat(10, 500, CV_8UC3, cv::Scalar(colorb, colorg, colorr)));
        }
        return;
    }

    for (int i = 0; i < 8; i++)
        childs[i]->search_color(palette);
}

void ColorNode::add_level(int height)
{
    if (level >= height)
    {
        isLeaf = true;
        return;
    }

    for (int i = 0; i < 8; i++)
    {
        childs[i] = new ColorNode(level + 1, 0, Color(), false);
        childs[i]->add_level(height);
    }
}

void ColorNode::delete_level()
{
    if (childs[0]->isLeaf)
    {
        for (int i = 0; i < 8; i++)
        {
            pixelCount += childs[i]->pixelCount;
            color.b += childs[i]->color.b;
            color.g += childs[i]->color.g;
            color.r += childs[i]->color.r;
            delete childs[i];
        }
        isLeaf = true;

        return;
    }

    for (int i = 0; i < 8; i++)
        childs[i]->delete_level();
}

class QuantizationOctree
{
private:
    int levels;
    ColorNode *root;

public:
    QuantizationOctree()
    {
        levels = 7;
        root = new ColorNode(7 - levels, 0, Color(), false);
        root->add_level(levels);
    }

    void fill(cv::Mat &image);
    void reduction();
    void reconstruction(cv::Mat &image);
    void get_palette(cv::Mat &palette);
    void search_color(ColorNode *path, ColorNode *aux);
    ~QuantizationOctree();
};

QuantizationOctree::~QuantizationOctree()
{
    delete root;
}

void QuantizationOctree::fill(cv::Mat &image)
{
    int channels = image.channels();

    int nRows = image.rows;
    int nCols = image.cols * channels;

    if (image.isContinuous())
    {
        nCols *= nRows;
        nRows = 1;
    }

    uchar *p;
    ColorNode *path;
    for (int i = 0; i < nRows; ++i)
    {
        p = image.ptr<uchar>(i);
        for (int j = 0; j < nCols; j += 3)
        {
            uchar b = p[j];
            uchar g = p[j + 1];
            uchar r = p[j + 2];
            path = root;

            for (int k = 0; k < levels; k++)
                path = path->childs[getIndex(r, g, b, k)];

            path->color.b += b;
            path->color.g += g;
            path->color.r += r;

            ++(path->pixelCount);
        }
    }
}

void QuantizationOctree::reduction()
{
    if (!levels)
        return;

    root->delete_level();
    --levels;
}

void QuantizationOctree::reconstruction(cv::Mat &image)
{
    int channels = image.channels();

    int nRows = image.rows;
    int nCols = image.cols * channels;

    // Imagen en forma 1 x n
    if (image.isContinuous())
    {
        nCols *= nRows;
        nRows = 1;
    }

    uchar *p;
    ColorNode *path;
    for (int i = 0; i < nRows; ++i)
    {
        p = image.ptr<uchar>(i);
        for (int j = 0; j < nCols; j += 3)
        {
            uchar b = p[j];
            uchar g = p[j + 1];
            uchar r = p[j + 2];
            path = root;

            for (uchar k = 0; k < levels; k++)
                path = path->childs[getIndex(r, g, b, k)];

            p[j] = (path->color.b) / (path->pixelCount);
            p[j + 1] = (path->color.g) / (path->pixelCount);
            p[j + 2] = (path->color.r) / (path->pixelCount);
        }
    }
}

void QuantizationOctree::get_palette(cv::Mat &palette)
{
    root->search_color(palette);
}