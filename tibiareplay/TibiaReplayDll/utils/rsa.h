#ifndef RSA_H_
#define RSA_H_

#include <cstddef>  // Needed due to bug in gmp.h, see https://gcc.gnu.org/gcc-4.9/porting_to.html
#include <gmp.h>

class RSA
{
 public:
  RSA();
  ~RSA();

  void setPrivateKey(const char* p, const char* q);
  void decrypt(char* msg);

 private:
  struct PublicKey
  {
    mpz_t n;  // Modulus
    mpz_t e;  // Public Exponent
  };

  struct PrivateKey
  {
    mpz_t n;  // Modulus
    mpz_t e;  // Public Exponent
    mpz_t d;  // Private Exponent
    mpz_t p;  // Starting prime p
    mpz_t q;  // Starting prime q
  };

  PublicKey public_key;
  PrivateKey private_key;

  mpz_t n_;
  mpz_t d_;
};

#endif  // RSA_H_
