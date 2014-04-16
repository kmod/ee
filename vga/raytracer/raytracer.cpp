// Simple OpenGL-based pixel renderer.
// Base OpenGL code taken from the MIT OCW 6.837 course, assignment 0

#include "GL/freeglut.h"

#include <cassert>
#include <cstdio>
#include <cmath>
#include <iostream>
#include <sstream>
#include <vector>

using namespace std;

struct Color {
    float r, g, b;
    constexpr Color(float r, float g, float b) : r(r), g(g), b(b) {}
};

struct Vector {
    float x, y, z;
    constexpr Vector(float x, float y, float z) : x(x), y(y), z(z) {}

    Vector cross(Vector rhs) const {
        return Vector(
            y * rhs.z - z * rhs.y,
            z * rhs.x - x * rhs.z,
            x * rhs.y - y * rhs.x
        );
    }

    float dot(Vector rhs) const {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }

    float magSquared() const {
        return x*x + y*y + z*z;
    }

    float mag() const {
        return sqrt(magSquared());
    }

    void normalize() {
        float m = mag();
        assert(m);
        x /= m;
        y /= m;
        z /= m;
    }

    Vector operator*(float rhs) const {
        return Vector(x * rhs, y * rhs, z * rhs);
    }
    Vector operator+(Vector rhs) const {
        return Vector(x + rhs.x, y + rhs.y, z + rhs.z);
    }
    void operator+=(Vector rhs) {
        x += rhs.x;
        y += rhs.y;
        z += rhs.z;
    }
    void operator-=(Vector rhs) {
        x -= rhs.x;
        y -= rhs.y;
        z -= rhs.z;
    }
    Vector operator-(Vector rhs) const {
        return Vector(x - rhs.x, y - rhs.y, z - rhs.z);
    }
    void print() const {
        printf("(%f, %f, %f) mag: %f\n", x, y, z, mag());
    }

    Vector rotateAround(Vector axis, float radians) const {
        axis.normalize();
        float v = dot(axis);
        Vector perp = (*this) - axis * v;
        float perp_mag = perp.mag();
        perp.normalize();

        Vector norm = axis.cross(perp);
        norm.normalize();

        Vector ang = perp * cos(radians) + norm * sin(radians);
        Vector r = ang * perp_mag + axis * v;
        return r;
    }
};
Vector operator*(float lhs, Vector rhs) {
    return Vector(lhs * rhs.x, lhs * rhs.y, lhs * rhs.z);
}

Vector camera(-3.0, 0.0, 1.0);
Vector look_dir(1.0, 0.0, -0.3);
Vector look_up(0.3, 0.0, 1.0);

Vector X(1.0, 0.0, 0.0);
Vector Y(0.0, 1.0, 0.0);
Vector Z(0.0, 0.0, 1.0);

class GeometryBase {
    public:
        virtual float intersectionTime(Vector start, Vector dir) = 0;
        virtual Color colorAt(Vector pos) = 0;
};

class Sphere : public GeometryBase {
    private:
        Vector center;
        float radius;

    public:
        Sphere(Vector center, float radius) : center(center), radius(radius) {}

        float intersectionTime(Vector start, Vector dir) override {
            //start.print();
            //dir.print();
            //printf("\n");

            Vector cp = center - start;
            float v = cp.dot(dir);
            float discriminant = (radius * radius) - (cp.dot(cp) - v*v);
            if (discriminant < 0)
                return -1;
            else
                return v - sqrt(discriminant);
        }

        Color colorAt(Vector pos) {
            Vector normal = pos - center;
            normal.normalize();

            float lightAmount = 0.8 * normal.dot(Z);
            if (lightAmount < 0)
                lightAmount = 0;
            lightAmount += 0.2;

            int t = (int)((pos.x - center.x) * 5) + (int)((pos.y - center.y) * 5) + (int)((pos.z - center.z) * 5) + radius * 10;
            if (t % 2 == 0)
                return Color(0, lightAmount, lightAmount);
            return Color(lightAmount, 0, lightAmount);
        }
};

std::vector<GeometryBase*> geometry;

// This function is called whenever a "Normal" key press is received.
void keyboardFunc( unsigned char key, int x, int y )
{
    Vector look_right = look_dir.cross(look_up);
    look_right.normalize();

    switch ( key ) {
        case 27: // Escape key
            exit(0);
            break;
        case 'q':
            look_up = look_up.rotateAround(look_dir, 0.1);
            look_up.normalize();
            break;
        case 'e':
            look_up = look_up.rotateAround(look_dir, -0.1);
            look_up.normalize();
            break;
        case 'a':
            camera -= look_right * 0.05;
            break;
        case 'A':
            camera -= look_right * 0.5;
            break;
        case 'd':
            camera += look_right * 0.05;
            break;
        case 'D':
            camera += look_right * 0.5;
            break;
        case 'w':
            camera += look_dir * 0.1;
            break;
        case 's':
            camera -= look_dir * 0.1;
            break;
        default:
            cout << "Unhandled key press " << key << "." << endl;        
    }

    glutPostRedisplay();
}

// This function is called whenever a "Special" key press is received.
// Right now, it's handling the arrow keys.
void specialFunc( int key, int x, int y )
{
    Vector look_right = look_dir.cross(look_up);
    look_right.normalize();

    //look_dir.print();
    //look_up.print();
    //look_right.print();

    switch ( key ) {
        case GLUT_KEY_UP:
            look_dir = look_dir.rotateAround(look_right, 0.1);
            look_up = look_up.rotateAround(look_right, 0.1);
            look_dir.normalize();
            look_up.normalize();
            break;
        case GLUT_KEY_DOWN:
            look_dir = look_dir.rotateAround(look_right, -0.1);
            look_up = look_up.rotateAround(look_right, -0.1);
            look_dir.normalize();
            look_up.normalize();
            break;
        case GLUT_KEY_LEFT:
            look_dir = look_dir.rotateAround(look_up, 0.1);
            look_dir.normalize();
            break;
        case GLUT_KEY_RIGHT:
            look_dir = look_dir.rotateAround(look_up, -0.1);
            look_dir.normalize();
            break;
    }

    glutPostRedisplay();
}

Color colorAt(Vector from, Vector direction) {
    GeometryBase *closest = NULL;
    float distance = 1e100;
    for (GeometryBase *g : geometry) {
        float d = g->intersectionTime(from, direction);
        if (d > 0 && d < distance) {
            distance = d;
            closest = g;
        }
    }
    if (closest) {
        return closest->colorAt(from + direction * distance);
    }
    return Color(0, 0, 0);
}

// This function is responsible for displaying the object.
void drawScene(void)
{
    int W = glutGet( GLUT_WINDOW_WIDTH );
    int H = glutGet( GLUT_WINDOW_HEIGHT );

    //double HEIGHT = 2.0; /// 90-degree FOV
    double HEIGHT = 1.73; /// 60-degree FOV

    Vector look_right = look_dir.cross(look_up);
    look_right.normalize();

    for (int r = 0; r < H; r++) {
        glBegin(GL_POINTS);
        for (int c = 0; c < W; c++) {
            //if (r == 5 || c == 5) {
                //glColor3f(1,1,1);
                //glVertex2f(c, r);
                //continue;
            //}

            float x = HEIGHT * (c - 0.5 * W) / H;
            float y = HEIGHT * (r - 0.5 * H) / H;

            Vector pixel_dir = look_dir + x * look_right + y * look_up;
            //Vector pixel_dir = look_dir.rotateAround(look_right, y).rotateAround(look_up, -x);
            pixel_dir.normalize();

            Color color = colorAt(camera, pixel_dir);

            glColor3f(color.r, color.g, color.b);
            glVertex2f(c, r);

        }
        glEnd();

        //if (r % 25 == 0)
            //glutSwapBuffers();
    }
    
    glutSwapBuffers();

    // Dump the image to the screen.


}

// Called when the window is resized
// w, h - width and height of the window in pixels.
void reshapeFunc(int w, int h)
{
    printf("reshape(%d, %d)\n", w, h);

    glMatrixMode (GL_PROJECTION);
    glLoadIdentity ();
    glViewport(0, 0, w, h);
    glOrtho (0, w, 0, h, -1, 1);

    glClear(GL_COLOR_BUFFER_BIT);

    glMatrixMode (GL_MODELVIEW);
    glLoadIdentity();
    glTranslatef(0.375, 0.375, 0);
}

// Main routine.
// Set up OpenGL, define the callbacks and start the main loop
int main( int argc, char** argv )
{
    geometry.push_back(new Sphere(Vector(0,0,0), 1.0));
    geometry.push_back(new Sphere(Vector(0,-1,0), 1.0));
    look_dir.normalize();
    look_up.normalize();

    glutInit(&argc,argv);

    // We're going to animate it, so double buffer 
    glutInitDisplayMode(GLUT_RGB);

    // Initial parameters for window position and size
    glutInitWindowSize( 300, 300 );

    glutCreateWindow("Testing");

    glDisable(GL_DEPTH_TEST);

    // Set up callback functions for key presses
    glutKeyboardFunc(keyboardFunc); // Handles "normal" ascii symbols
    glutSpecialFunc(specialFunc);   // Handles "special" keyboard keys

     // Set up the callback function for resizing windows
    glutReshapeFunc( reshapeFunc );

    // Call this whenever window needs redrawing
    glutDisplayFunc( drawScene );

    glClear(GL_COLOR_BUFFER_BIT);
    // Start the main loop.  glutMainLoop never returns.
    glutMainLoop( );

    return 0;	// This line is never reached.
}

