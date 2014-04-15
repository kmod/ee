// Simple OpenGL-based pixel renderer.
// Base OpenGL code taken from the MIT OCW 6.837 course, assignment 0

#include "GL/freeglut.h"

#include <cstdio>
#include <cmath>
#include <iostream>
#include <sstream>
#include <vector>

using namespace std;

// This function is called whenever a "Normal" key press is received.
void keyboardFunc( unsigned char key, int x, int y )
{
    switch ( key )
    {
    case 27: // Escape key
        exit(0);
        break;
    case 'c':
        // add code to change color here
		cout << "Unhandled key press " << key << "." << endl; 
        break;
    default:
        cout << "Unhandled key press " << key << "." << endl;        
    }

    glutPostRedisplay();
}

static int iters = 10;

// This function is called whenever a "Special" key press is received.
// Right now, it's handling the arrow keys.
void specialFunc( int key, int x, int y )
{
    switch ( key )
    {
    case GLUT_KEY_UP:
        iters++;
		break;
    case GLUT_KEY_DOWN:
        iters--;
		break;
    case GLUT_KEY_LEFT:
		break;
    case GLUT_KEY_RIGHT:
		break;
    }

    glutPostRedisplay();
}

void colorAt(double x, double y) {
    x = 2 * x;
    y = 2 * y;
    double zx = 0;
    double zy = 0;

    for (int i = 0; i < iters; i++) {
        //printf("%d %.3f %.3f\n", i, zx, zy);
        double tx = zx * zx - zy * zy;
        double ty = 2.0 * zx * zy;
        zx = tx + x;
        zy = ty + y;

        if (fabs(zx) >= 5 || fabs(zy) >= 5) {
            double d = i * 0.04;
            glColor3f(d * 0.3, d, d*2);
            return;
        }
    }

    glColor3f(0, 0, 0);

    //glColor3f(x, y, 1.0);
    //glColor3f(c * 1.0 / W, r * 1.0 / H, (renders % 5 ) / 5.0);
}

// This function is responsible for displaying the object.
void drawScene(void)
{
    // Clear the rendering window
    //colorAt(-0.25, 0.25);
    //return;

    int W = 100;
    int H = 100;
    W = glutGet( GLUT_WINDOW_WIDTH );
    H = glutGet( GLUT_WINDOW_HEIGHT );

    static int renders = 0;
    renders++;

    double HEIGHT = 2.0;

    for (int r = 0; r < H; r++) {
        glBegin(GL_POINTS);
        for (int c = 0; c < W; c++) {
            colorAt(HEIGHT * (c - 0.5 * W) / H, HEIGHT * (r - 0.5 * H) / H);

            glVertex2f(c, r);

        }
        glEnd();

        if (r % 25 == 0)
            glutSwapBuffers();
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
    glOrtho (0, w, h, 0, -1, 1);

    glClear(GL_COLOR_BUFFER_BIT);

    glMatrixMode (GL_MODELVIEW);
    glLoadIdentity();
    glTranslatef(0.375, 0.375, 0);
}

// Main routine.
// Set up OpenGL, define the callbacks and start the main loop
int main( int argc, char** argv )
{
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
